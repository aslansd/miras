"""Can this study design recover these parameters?

`identify` simulates pseudo-observed datasets from known parameter values,
infers the parameters back, and reports what the design cannot do:

EQUIFINALITY (i, j)
    Different combinations of i and j produce indistinguishable data. The data
    pin down a combination of the two (the posterior is a narrow ridge) but not
    each parameter separately.
NOT_IDENTIFIED (j)
    The posterior for j is essentially the prior coming back: the data carry
    almost no information about j, even jointly with other parameters.

Everything is measured on each prior's working scale, standardised by the
prior SD, so "contraction" = 1 - posterior variance / prior variance is
comparable across parameters (0 = learned nothing, 1 = pinned down exactly).

`analyze` does the measurement for posteriors from any backend (e.g. Stan);
`identify` also runs the simulations and ABC inference.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field

import numpy as np

from .inference.abc import ABCSMC, Posterior, ReferenceTable
from .inference.priors import as_priors
from .inference.simulators import as_simulator, run_batch, seeds_for


@dataclass(frozen=True)
class Thresholds:
    """Decision rules. The defaults are pinned by the sensitivity/specificity
    tests in tests/test_identify.py."""

    not_identified: float = 0.2      # mean contraction below this -> NOT_IDENTIFIED
    anisotropy: float = 0.15         # ridge: smallest/largest posterior variance below this
    across_ridge: float = 0.5        # ridge: contraction across the ridge at least this
    mixing: float = 0.3              # ridge direction loads >= this on both parameters
    joint_gain: float = 0.25         # combination learned this much better than either marginal
    min_fraction: float = 0.3        # fraction of test datasets showing the ridge
    high_fraction: float = 0.6       # ... above which severity is "high"
    min_region: int = 12             # test datasets needed in a region to judge it


@dataclass
class Finding:
    id: str
    severity: str
    params: list
    what: str
    evidence: dict = field(default_factory=dict)
    where: str = ""                  # "" = across the whole prior; else a region


@dataclass
class IdentifiabilityReport:
    parameters: list
    findings: list
    info: dict
    details: dict = field(repr=False, default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.findings

    def summary(self) -> str:
        lines = [f"Identifiability report ({self.info.get('method', '?')}, "
                 f"{self.info.get('n_test', '?')} test datasets)"]
        if self.info.get("summaries"):
            lines.append(f"summaries: {', '.join(self.info['summaries'])}")
        lines.append("")
        lines.append(f"{'parameter':<24}{'contraction':>12}{'90% coverage':>14}{'bias (sd)':>11}")
        for p in self.parameters:
            lines.append(f"{p['name']:<24}{p['contraction']:>12.2f}{p['coverage90']:>14.2f}"
                         f"{p['bias']:>+11.2f}")
        lines.append("")
        if not self.findings:
            lines.append("No findings.")
            weak = [p["name"] for p in self.parameters if p["contraction"] < 0.5]
            if weak:
                lines.append(f"Only partly constrained (contraction < 0.5): {', '.join(weak)}.")
        for f in self.findings:
            where = f" (where {f.where})" if f.where else ""
            lines.append(f"[{f.severity}] {f.id} {', '.join(f.params)}{where}")
            lines.append(f"    {f.what}")
        cov = [p["coverage90"] for p in self.parameters]
        if cov and min(cov) < 0.75:
            lines.append("")
            lines.append("note: 90% intervals cover the truth less than 75% of the time for some "
                         "parameters; the inference itself may be miscalibrated (more simulations, "
                         "a larger accept fraction or ABC-SMC may help).")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {"parameters": self.parameters, "findings": [asdict(f) for f in self.findings],
                "info": self.info}

    def to_json(self, path=None, **kw):
        s = json.dumps(self.to_dict(), indent=2, default=float, **kw)
        if path:
            with open(path, "w") as fh:
                fh.write(s)
        return s

    def to_markdown(self) -> str:
        out = ["# Identifiability report", ""]
        for k in ("method", "n_test", "n_reference", "summaries"):
            if k in self.info:
                v = self.info[k]
                out.append(f"- **{k}**: {', '.join(v) if isinstance(v, (list, tuple)) else v}")
        out += ["", "| parameter | contraction | 90% coverage | bias (prior sd) |", "|---|---|---|---|"]
        for p in self.parameters:
            out.append(f"| `{p['name']}` | {p['contraction']:.2f} | {p['coverage90']:.2f} | {p['bias']:+.2f} |")
        out += ["", "## Findings", ""]
        if not self.findings:
            out.append("None.")
        for f in self.findings:
            where = f" *where {f.where}*" if f.where else ""
            out.append(f"- **{f.id}** ({f.severity}) `{'`, `'.join(f.params)}`{where}: {f.what}")
        return "\n".join(out) + "\n"

    def plot(self, path=None, pair=None):
        """Contraction per parameter, and posterior means vs. truth for one
        parameter pair (the first equifinal pair by default)."""
        import matplotlib
        if path:
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        names = [p["name"] for p in self.parameters]
        eq = [f for f in self.findings if f.id == "EQUIFINALITY"]
        if pair is None:
            pair = eq[0].params if eq else names[:2]
        fig, axes = plt.subplots(1, 2 if len(names) > 1 else 1, figsize=(10, 4), squeeze=False)
        ax = axes[0, 0]
        c = [p["contraction"] for p in self.parameters]
        ax.barh(names, c, color=["#E41A1C" if v < 0.2 else "#377EB8" for v in c])
        ax.axvline(0.2, ls="--", color="grey")
        ax.set_xlim(min(0, min(c)), 1)
        ax.set_xlabel("posterior contraction (0 = prior, 1 = exact)")
        ax.invert_yaxis()
        if len(names) > 1:
            ax = axes[0, 1]
            i, j = names.index(pair[0]), names.index(pair[1])
            T = self.details["truths_x"]
            ax.scatter(T[:, i], T[:, j], s=12, color="lightgrey", label="all test truths")
            k = int(np.argmin(self.details["contraction"][:, [i, j]].sum(1)))
            samp = self.details["example_samples"][k]
            ax.scatter(samp[:, i], samp[:, j], s=6, alpha=0.4, color="#377EB8",
                       label="posterior (one dataset)")
            ax.scatter(T[k, i], T[k, j], s=80, color="#E41A1C", marker="*", label="truth")
            ax.set_xlabel(pair[0])
            ax.set_ylabel(pair[1])
            ax.legend(fontsize=8, framealpha=0.85, loc="upper left", bbox_to_anchor=(1.01, 1))
            ax.set_title("EQUIFINALITY" if eq else "posterior for the least-constrained dataset",
                         fontsize=10)
        fig.tight_layout()
        if path:
            fig.savefig(path, dpi=150)
            plt.close(fig)
        return fig


# --------------------------------------------------------------------------- #
def _weighted_quantile(x, w, q):
    o = np.argsort(x)
    cw = np.cumsum(w[o])
    return np.interp(q, cw - w[o] / 2, x[o])


def analyze(priors, truths_u, posteriors, *, thresholds=None, info=None, n_example=300,
            rng=None) -> IdentifiabilityReport:
    """Measure identifiability from posteriors of pseudo-observed datasets.

    Parameters
    ----------
    priors : dict or Priors
    truths_u : (n_test, p) true parameter values on the working (u) scale
    posteriors : list of `Posterior` (or (U, weights) tuples), one per test dataset
    """
    th = thresholds or Thresholds()
    pr = as_priors(priors)
    rng = rng or np.random.default_rng(0)
    T = np.atleast_2d(np.asarray(truths_u, float))
    names, p = pr.names, len(pr)
    sd = pr.sd_u
    n = len(posteriors)

    contraction = np.zeros((n, p))
    covered = np.zeros((n, p), bool)
    bias = np.zeros((n, p))
    covs = np.zeros((n, p, p))
    examples = []
    for t, post in enumerate(posteriors):
        if not isinstance(post, Posterior):
            post = Posterior(pr, *post)
        S = post.cov_u() / np.outer(sd, sd)
        covs[t] = S
        contraction[t] = 1.0 - np.diag(S)
        mean_u = post.weights @ post.U
        bias[t] = (mean_u - T[t]) / sd
        for j in range(p):
            lo, hi = _weighted_quantile(post.U[:, j], post.weights, [0.05, 0.95])
            covered[t, j] = lo <= T[t, j] <= hi
        idx = rng.choice(len(post.weights), min(n_example, len(post.weights)), p=post.weights)
        examples.append(pr.to_x(post.U[idx]))

    params = [{"name": names[j], "contraction": float(contraction[:, j].mean()),
               "coverage90": float(covered[:, j].mean()), "bias": float(bias[:, j].mean())}
              for j in range(p)]

    def ridge_flags(i, j, rows):
        flags, dirs = [], []
        for t in rows:
            sub = covs[t][np.ix_([i, j], [i, j])]
            lam, vec = np.linalg.eigh(sub)
            lmin, lmax = max(lam[0], 1e-12), max(lam[1], 1e-12)
            v = vec[:, 1]
            ok = (lmin / lmax < th.anisotropy and 1 - lmin >= th.across_ridge
                  and min(abs(v[0]), abs(v[1])) >= th.mixing
                  and (1 - lmin) - max(contraction[t, i], contraction[t, j]) >= th.joint_gain)
            flags.append(ok)
            if ok:
                dirs.append(v if v[0] >= 0 else -v)
        return (float(np.mean(flags)) if flags else 0.0), dirs

    def equifinality(i, j, rows, where):
        frac, dirs = ridge_flags(i, j, rows)
        if frac < th.min_fraction:
            return None
        v = np.mean(dirs, axis=0)
        slope = (v[1] * sd[j]) / (v[0] * sd[i])
        trade = "raising" if slope > 0 else "lowering"
        what = (f"The data constrain a combination of {names[i]} and {names[j]} but not each "
                f"separately: raising {names[i]}{_scale_word(pr.priors[i])} can be offset by "
                f"{trade} {names[j]}{_scale_word(pr.priors[j])} ({slope:+.3g} per unit) with no "
                f"visible change in the summaries. Seen in {frac:.0%} of test datasets"
                f"{' in this region' if where else ''}. Add summaries sensitive to one parameter "
                f"but not the other, or fix one from independent data.")
        return Finding("EQUIFINALITY", "high" if frac >= th.high_fraction else "warning",
                       [names[i], names[j]], what,
                       {"fraction": frac, "slope_u": float(slope), "direction_z": v.tolist(),
                        "n": len(rows)}, where)

    def not_identified(j, rows, where):
        c = float(contraction[rows, j].mean())
        if c >= th.not_identified:
            return None
        return Finding(
            "NOT_IDENTIFIED", "high" if c < th.not_identified / 2 and not where else "warning",
            [names[j]],
            f"The posterior for {names[j]} is close to its prior (contraction {c:.2f}"
            f"{' in this region' if where else ''}): these summaries carry little information "
            f"about it, alone or in combination with other parameters.",
            {"contraction": c, "n": len(rows)}, where)

    findings = []
    everyone = np.arange(n)
    pairs = [(i, j) for i in range(p) for j in range(i + 1, p)]

    # across the whole prior
    for i, j in pairs:
        f = equifinality(i, j, everyone, "")
        if f:
            findings.append(f)
    equifinal = {q for f in findings for q in f.params}
    for j in range(p):
        if names[j] not in equifinal:
            f = not_identified(j, everyone, "")
            if f:
                findings.append(f)

    # in regions: thirds of each parameter's prior range (on the working scale).
    # A problem confined to part of parameter space is averaged away globally.
    # Adjacent failing thirds are merged into one range.
    flagged = {(f.id, tuple(f.params)) for f in findings}
    lo_u, hi_u = T.min(axis=0), T.max(axis=0)

    def describe(k, bounds):
        a = max(bounds[0], lo_u[k])
        b = min(bounds[1], hi_u[k])
        xa = pr.priors[k].from_u(np.array([a]))[0]
        xb = pr.priors[k].from_u(np.array([b]))[0]
        if bounds[0] == -np.inf:
            return f"{names[k]} < {xb:.3g}"
        if bounds[1] == np.inf:
            return f"{names[k]} > {xa:.3g}"
        return f"{xa:.3g} < {names[k]} < {xb:.3g}"

    def merged(k, failing):
        """failing: sorted region indices 0..2 -> 'where' text for contiguous runs."""
        runs, cur = [], [failing[0]]
        for r in failing[1:]:
            if r == cur[-1] + 1:
                cur.append(r)
            else:
                runs.append(cur)
                cur = [r]
        runs.append(cur)
        return " or ".join(describe(k, (cuts[k][run[0]], cuts[k][run[-1] + 1])) for run in runs)

    cuts = {}
    for k in range(p):
        e = np.quantile(T[:, k], [1 / 3, 2 / 3])
        cuts[k] = [-np.inf, e[0], e[1], np.inf]
        regions = [np.flatnonzero((T[:, k] > cuts[k][r]) & (T[:, k] <= cuts[k][r + 1]))
                   for r in range(3)]
        usable = [r for r in range(3) if regions[r].size >= th.min_region]
        checks = [("EQUIFINALITY", (i, j)) for i, j in pairs] + \
                 [("NOT_IDENTIFIED", (j,)) for j in range(p)]
        for kind, idx in checks:
            key = (kind, tuple(names[q] for q in idx))
            if key in flagged or (kind == "NOT_IDENTIFIED" and names[idx[0]] in equifinal):
                continue
            hits = {}
            for r in usable:
                f = (equifinality(*idx, regions[r], "x") if kind == "EQUIFINALITY"
                     else not_identified(idx[0], regions[r], "x"))
                if f:
                    hits[r] = f
            if not hits:
                continue
            failing = sorted(hits)
            rows = np.concatenate([regions[r] for r in failing])
            where = merged(k, failing)
            f = (equifinality(*idx, rows, where) if kind == "EQUIFINALITY"
                 else not_identified(idx[0], rows, where))
            if f is None:            # pooled regions can fall just short; report the worst one
                f = hits[failing[0]]
                f.where = merged(k, [failing[0]])
            findings.append(f)
            flagged.add(key)

    details = {"truths_u": T, "truths_x": pr.to_x(T), "contraction": contraction,
               "covered": covered, "bias": bias, "cov_z": covs, "example_samples": examples}
    return IdentifiabilityReport(params, findings, dict(info or {}, n_test=n), details)


def _scale_word(prior):
    from .inference.priors import LogUniform, Normal
    if isinstance(prior, LogUniform) or (isinstance(prior, Normal) and prior.transform == "log"):
        return " (on the log scale)"
    if isinstance(prior, Normal) and prior.transform == "logit":
        return " (on the logit scale)"
    return ""


def identify(simulator, priors, *, method="rejection", n_reference=2000, n_test=50,
             accept=0.05, adjust=True, smc=None, seed=0, cores=1, table=None,
             thresholds=None, track=False, label="miras-identify") -> IdentifiabilityReport:
    """Simulate pseudo-observed datasets, infer their parameters, and report
    what this simulator + design cannot recover.

    method="rejection" (default) builds one reference table of `n_reference`
    prior simulations and uses `n_test` of its rows as pseudo-observed data,
    each analysed against the rest (ABC cross-validation). Cheap: one set of
    simulations serves every test dataset. Pass a prebuilt `table` to reuse it.

    method="smc" draws `n_test` truths from the prior and runs ABC-SMC on each
    (keyword arguments in `smc`). Sharper, but costs thousands of simulations
    per test dataset.

    track=True records the run with daftar (if installed).
    """
    from .provenance import tracked

    sim = as_simulator(simulator)
    pr = as_priors(priors)
    names = (table.summary_names if table is not None and table.summary_names
             else getattr(sim, "summary_names", None))
    info = {"method": method, "summaries": list(names or []),
            "priors": {n: repr(p) for n, p in zip(pr.names, pr.priors)}}
    if hasattr(sim, "describe"):
        info["simulator"] = sim.describe()
    params = {"method": method, "n_reference": n_reference, "n_test": n_test,
              "accept": accept, "adjust": adjust, **{f"prior.{k}": v for k, v in info["priors"].items()},
              "summaries": ",".join(info["summaries"])}

    with tracked(label, params=params, seed=seed, enabled=track) as run:
        if method == "rejection":
            if table is None:
                table = ReferenceTable.build(sim, pr, n_reference, seed=seed, cores=cores)
            n_test = min(n_test, len(table) // 2)
            test_idx = np.arange(n_test)
            posts = [table.posterior(table.S[i], accept=accept, adjust=adjust, exclude=i)
                     for i in test_idx]
            truths = table.U[test_idx]
            info.update(n_reference=len(table), accept=accept, adjusted=adjust)
        elif method == "smc":
            rng = np.random.default_rng(seed)
            truths = pr.sample_u(rng, n_test)
            X = pr.to_x(truths)
            obs = run_batch(sim, [pr.as_dict(x) for x in X], seeds_for(seed + 7, n_test), cores)
            smc_kw = dict(smc or {})
            posts = [ABCSMC(sim, pr, cores=cores, **smc_kw).run(o, seed=seed + 100 + t)
                     for t, o in enumerate(obs)]
            info.update(n_simulations=int(sum(p.info["n_simulations"] for p in posts)), smc=smc_kw)
        else:
            raise ValueError("method must be 'rejection' or 'smc'")

        report = analyze(pr, truths, posts, thresholds=thresholds, info=info)
        run.log_results({f"contraction.{p['name']}": p["contraction"] for p in report.parameters})
        run.log_results({f"coverage90.{p['name']}": p["coverage90"] for p in report.parameters})
        run.log_result("n_findings", len(report.findings))
        run.log_result("findings", ";".join(f"{f.id}({','.join(f.params)})" for f in report.findings))
    return report
