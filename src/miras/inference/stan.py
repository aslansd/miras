"""Stan backend (via CmdStanPy). Optional: pip install "miras[stan]", then
install CmdStan once with the ``install_cmdstan`` command.

Every fit is checked for convergence. A fit that has not converged is
reported loudly, with the chains responsible, because a stuck chain silently
mixed into a posterior is worse than no posterior (see `assess_chains`).
"""
from __future__ import annotations

import hashlib
import os
import shutil
import sys
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path

import numpy as np

INSTALL_HINT = (
    "Install CmdStan once with the `install_cmdstan` command (a few minutes; on macOS "
    "run `xcode-select --install` first). If the download fails with "
    "SSL: CERTIFICATE_VERIFY_FAILED, run `export SSL_CERT_FILE=\"$(python -m certifi)\"` "
    "and retry, or run the 'Install Certificates.command' that came with your Python. "
    "Check with `miras doctor`."
)

# A fit counts as converged when every R-hat is at most this and there are no
# divergent transitions (the usual Stan recommendations).
RHAT_MAX = 1.01


def stan_file(name: str) -> str:
    """Path of a Stan model shipped with miras (e.g. 'Longitudinal_Conf')."""
    return str(resources.files("miras.stan").joinpath(f"{name}.stan"))


def cache_dir() -> Path:
    """Where compiled models live: $MIRAS_CACHE, else ~/.cache/miras."""
    root = os.environ.get("MIRAS_CACHE") or os.path.join(
        os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")), "miras")
    return Path(root) / "stan"


def _compilable_copy(name: str) -> str:
    """CmdStan writes the executable next to the .stan file, and an installed
    package directory may be read-only, so compile from a copy in the user
    cache. The copy is keyed by content hash, so an edited model recompiles."""
    src = Path(stan_file(name))
    digest = hashlib.sha256(src.read_bytes()).hexdigest()[:12]
    dst = cache_dir() / f"{name}-{digest}.stan"
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    return str(dst)


def cmdstan_available() -> tuple[bool, str]:
    try:
        import cmdstanpy
    except ImportError:
        return False, "cmdstanpy not installed (pip install 'miras[stan]')"
    try:
        path = cmdstanpy.cmdstan_path()
    except Exception:
        return False, "CmdStan not installed. " + INSTALL_HINT
    return True, path


def sample(name: str, data, *, seed=1, chains=4, iter_warmup=1000, iter_sampling=1000,
           output_dir=None, init_radius=None, **kwargs):
    """Compile (cached) and sample a packaged Stan model.

    init_radius: chains start uniformly in (-r, r) on the unconstrained scale.
    None keeps Stan's default (r = 2); smaller values start chains closer
    together, which can keep a chain from starting in a pathological region.
    """
    ok, msg = cmdstan_available()
    if not ok:
        raise RuntimeError(msg)
    from cmdstanpy import CmdStanModel
    model = CmdStanModel(stan_file=_compilable_copy(name))
    if init_radius is not None:
        kwargs["inits"] = float(init_radius)
    return model.sample(data=data, seed=seed, chains=chains, parallel_chains=chains,
                        iter_warmup=iter_warmup, iter_sampling=iter_sampling,
                        output_dir=output_dir, **kwargs)


# --------------------------------------------------------------------------- #
# Convergence
# --------------------------------------------------------------------------- #
@dataclass
class Convergence:
    """Diagnostics of one fit.

    converged: max R-hat <= 1.01 and no divergent transitions.
    suspect_chains: chains that look stuck (0-based): mostly divergent, or
    with a posterior mean far from all the other chains.
    """

    max_rhat: float
    divergences: int
    per_chain_divergences: list
    per_chain_means: dict
    suspect_chains: list
    n_draws_per_chain: int
    converged: bool
    reasons: list = field(default_factory=list)

    def as_dict(self):
        return {"max_rhat": self.max_rhat, "divergences": self.divergences,
                "per_chain_divergences": self.per_chain_divergences,
                "suspect_chains": self.suspect_chains, "converged": self.converged}

    def line(self) -> str:
        return f"max R-hat = {self.max_rhat:.3f}, divergent transitions = {self.divergences}"

    def report(self) -> str:
        """Multi-line explanation for a fit that did not converge."""
        if self.converged:
            return f"converged ({self.line()})"
        lines = ["WARNING: the Stan fit did NOT converge; do not use its posterior as is.",
                 f"  {self.line()}  (need R-hat <= {RHAT_MAX} and 0 divergences)"]
        names = list(self.per_chain_means)
        head = "  chain  divergences  " + "  ".join(f"{n:>12}" for n in names)
        lines.append(head)
        for c, dv in enumerate(self.per_chain_divergences):
            means = "  ".join(f"{self.per_chain_means[n][c]:>12.3f}" for n in names)
            flag = "   <- suspect" if c in self.suspect_chains else ""
            lines.append(f"  {c + 1:>5}  {dv:>11}  {means}{flag}")
        for r in self.reasons:
            lines.append(f"  - {r}")
        lines.append("  What to do: refit with another seed and/or a smaller --init-radius "
                     "(e.g. 0.5); more warm-up can also help. See README, 'Convergence "
                     "of the longitudinal fit'.")
        return "\n".join(lines)


def assess_chains(draws: np.ndarray, divergent: np.ndarray, max_rhat: float,
                  names=None, stuck_fraction=0.5, far_sd=4.0) -> Convergence:
    """Assess convergence from raw draws.

    draws: (n_draws, n_chains, n_params) post-warm-up draws of key parameters.
    divergent: (n_draws, n_chains) 0/1 divergence indicators.
    A chain is suspect if more than `stuck_fraction` of its iterations diverged,
    or if, for any parameter, its mean is more than `far_sd` pooled
    within-chain SDs away from the median of the other chains' means.
    """
    draws = np.asarray(draws, float)
    divergent = np.asarray(divergent)
    n, C, P = draws.shape
    names = list(names) if names is not None else [f"p{j}" for j in range(P)]
    per_div = divergent.sum(axis=0).astype(int).tolist()
    means = draws.mean(axis=0)                                   # (C, P)
    sds = draws.std(axis=0, ddof=1)                              # (C, P)
    suspect, reasons = [], []
    for c in range(C):
        if per_div[c] > stuck_fraction * n:
            suspect.append(c)
            reasons.append(f"chain {c + 1} diverged on {per_div[c]} of {n} iterations "
                           f"(it is stuck, not sampling)")
            continue
        if C < 3:
            continue
        others = [k for k in range(C) if k != c]
        for j in range(P):
            ref = np.median(means[others, j])
            pooled = np.sqrt(np.mean(sds[others, j] ** 2)) or 1e-12
            if abs(means[c, j] - ref) > far_sd * pooled:
                suspect.append(c)
                reasons.append(f"chain {c + 1} is far from the others in {names[j]} "
                               f"(mean {means[c, j]:.3g} vs {ref:.3g})")
                break
    divs = int(sum(per_div))
    converged = bool(max_rhat <= RHAT_MAX and divs == 0)
    if not converged and not suspect:
        reasons.append("no single chain stands out: the whole fit is struggling "
                       "(try more warm-up or check the model/data)")
    return Convergence(float(max_rhat), divs, per_div,
                       {nm: means[:, j].tolist() for j, nm in enumerate(names)},
                       suspect, n, converged, reasons)


def convergence(fit, params=None) -> Convergence:
    """Diagnostics of a CmdStanPy fit. `params` are the scalar parameters whose
    per-chain means are compared (default: all scalar parameters)."""
    summ = fit.summary()
    col = [c for c in summ.columns if "R_hat" in c][0]
    max_rhat = float(np.nanmax(summ[col].to_numpy()))
    cols = list(fit.column_names)
    raw = fit.draws()                                            # (draws, chains, columns)
    if params is None:
        params = [c for c in cols if not c.endswith("__") and "[" not in c and "." not in c]
    params = [p for p in params if p in cols]
    draws = raw[:, :, [cols.index(p) for p in params]]
    divergent = raw[:, :, cols.index("divergent__")]
    return assess_chains(draws, divergent, max_rhat, names=params)


def warn_if_unconverged(diag: Convergence, stream=None) -> None:
    stream = stream or sys.stderr
    if not diag.converged:
        print(diag.report(), file=stream, flush=True)
