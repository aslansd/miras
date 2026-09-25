"""Stan backend (via CmdStanPy). Optional: pip install "miras[stan]" and run
``python -m cmdstanpy.install_cmdstan`` once."""
from __future__ import annotations

import hashlib
import os
import shutil
from importlib import resources
from pathlib import Path

import numpy as np


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
    except Exception as exc:
        return False, f"CmdStan not installed ({exc}); run: python -m cmdstanpy.install_cmdstan"
    return True, path


def sample(name: str, data, *, seed=1, chains=4, iter_warmup=1000, iter_sampling=1000,
           output_dir=None, **kwargs):
    """Compile (cached by CmdStan) and sample a packaged Stan model."""
    ok, msg = cmdstan_available()
    if not ok:
        raise RuntimeError(msg)
    from cmdstanpy import CmdStanModel
    model = CmdStanModel(stan_file=_compilable_copy(name))
    return model.sample(data=data, seed=seed, chains=chains, parallel_chains=chains,
                        iter_warmup=iter_warmup, iter_sampling=iter_sampling,
                        output_dir=output_dir, **kwargs)


def convergence(fit) -> dict:
    """Compact diagnostics: max R-hat and number of divergent transitions."""
    summ = fit.summary()
    col = [c for c in summ.columns if "R_hat" in c][0]
    return {"max_rhat": float(np.nanmax(summ[col].to_numpy())),
            "divergences": int(fit.method_variables()["divergent__"].sum())}
