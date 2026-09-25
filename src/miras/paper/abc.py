"""
Deffner, D., Fedorova, N., Andrews, J. & McElreath, R.
Bridging theory and data: A computational workflow for cultural evolution
Approximate Bayesian Computation
(R original by N. Fedorova, ABC_analysis.R; ported to miras)

Simulates cross-sectional data on cultural Fst for hypothetical populations
(one with unbiased, one with conformist transmission), infers migration rate m
and conformity exponent theta with rejection ABC, runs posterior predictions
and migration contrasts, and plots Fig. 5.

ABC is computationally heavy: the default of 100,000 simulations per analysis
matches the paper. Use --n-comb to reduce (and --n-accept accordingly).

This reproduces the paper's discrete-grid rejection ABC. For the general
question it raises -- can F_ST alone separate conformity from migration? --
see miras.identify and examples/equifinality.py.

Usage:
    miras paper abc --cores 32
    miras paper abc --n-comb 5000 --n-accept 100 --cores 8
    miras paper abc --reuse           # re-plot from cached results
"""
import argparse
import os
import pickle
import time
import warnings
from multiprocessing import Pool

import numpy as np
import pandas as pd

from ._model import paper_model
from ._plot import SET1, alpha, color_ramp, r_density
from ..provenance import tracked


def spawn_rngs(seed, n):
    return [np.random.default_rng(s) for s in np.random.SeedSequence(seed).spawn(n)]

N_GROUPS = 30
MAX_AGE = 90
M_GRID = np.round(np.arange(0.0, 0.4 + 1e-9, 0.1), 10)   # flat prior on migration rate
THETA_GRID = np.array([0.5, 1.0, 2.0, 3.0])               # flat prior on conformity exponent

def mig_abm(rng, N=3000, n_groups=N_GROUPS, n_steps=100, n_burn_in=1000,
            n_mod=30, m_const=0.1, mu=0.1, theta=1.3, r_dist=0.2, legacy_aging=False):
    """Cultural evolution model with age-dependent learning and migration.

    Returns (Fst, total variance, between-group variance), one value per year.

    Note: the R function lists the learner's own variant among the candidate
    variants but counts frequencies among role models only, so the own variant
    has weight zero unless a model also holds it. That is identical to plain
    model-based transmission, which is what Conformity(include_self=False) implements."""
    model = paper_model(theta=theta, m=m_const, mu=mu, max_age=MAX_AGE, n_groups=n_groups,
                        group_size=N // n_groups, n_models=n_mod, r_dist=r_dist,
                        legacy_aging=legacy_aging)
    out = model.simulate(n_steps, burn_in=n_burn_in, rng=rng,
                         record=("fst", "total_diversity", "within_diversity")).series
    return out["fst"], out["total_diversity"], out["total_diversity"] - out["within_diversity"]


def _abc_job(args):
    """abc_loop_fst: simulate and compare the last year with the reference."""
    row, ref_last, fst_compare, rng, legacy = args
    fst, tot, btw = mig_abm(rng, legacy_aging=legacy, **row)
    if fst_compare:
        return fst[-1] - ref_last[0]
    return abs(tot[-1] - ref_last[1]) + abs(btw[-1] - ref_last[2])


def _pred_job(args):
    row, rng, legacy = args
    return mig_abm(rng, legacy_aging=legacy, **row)[0][-1]


def make_jobs(rng, n_comb, n_steps, n_burn_in):
    """Parameter combinations drawn from flat priors on m and theta."""
    return pd.DataFrame(dict(
        N=3000, n_groups=N_GROUPS, n_steps=n_steps, n_burn_in=n_burn_in, n_mod=30,
        m_const=rng.choice(M_GRID, n_comb), mu=0.05,
        theta=rng.choice(THETA_GRID, n_comb), r_dist=0.0,
    ))


def _rows(df):
    return [{k: (float(v) if isinstance(v, float) else int(v)) for k, v in r.items()}
            for r in df.to_dict("records")]


def run_abc(pool, jobs, reference, seed, legacy):
    ref_last = (reference[0][-1], reference[1][-1], reference[2][-1])
    tasks = [(r, ref_last, True, g, legacy) for r, g in zip(_rows(jobs), spawn_rngs(seed, len(jobs)))]
    out, t0 = [], time.time()
    for k, d in enumerate(pool.imap(_abc_job, tasks, chunksize=8), 1):
        out.append(d)
        if k % 100 == 0 or k == len(tasks):
            print(f"  {k}/{len(tasks)} ({time.time() - t0:.0f}s)", flush=True)
    return np.array(out)


def rejection(jobs, diffs, n_accept):
    """Keep the n_accept parameter combinations closest to the reference Fst."""
    df = jobs.copy()
    df["abc_diff"] = diffs
    df["absolute_diff"] = np.abs(diffs)
    return df.sort_values("absolute_diff", kind="stable").head(n_accept).reset_index(drop=True)


def first_n(df, n, label):
    """R takes rows 1..n; if fewer exist R would produce NA rows and fail.
    Here we resample with replacement (with a warning) instead."""
    if len(df) == 0:
        warnings.warn(f"{label}: no posterior samples, contrast skipped")
        return None
    if len(df) < n:
        warnings.warn(f"{label}: only {len(df)} posterior samples; resampling to {n}")
        return df.sample(n, replace=True, random_state=0).reset_index(drop=True)
    return df.head(n)


def predict(pool, df, seed, legacy):
    if df is None:
        return None
    params = df[["N", "n_groups", "n_steps", "n_burn_in", "n_mod", "m_const", "mu", "theta", "r_dist"]]
    tasks = [(r, g, legacy) for r, g in zip(_rows(params), spawn_rngs(seed, len(df)))]
    return np.array(pool.map(_pred_job, tasks))


def shift_m(df, delta):
    out = df.copy()
    out["m_const"] = np.round(out["m_const"] + delta, 10)
    return out


# --------------------------------------------------------------------------- #
# Plot (Fig. 5)
# --------------------------------------------------------------------------- #
def joint_posterior_panel(ax, post, true_theta, true_m, label):
    tab = pd.crosstab(post["m_const"], post["theta"]).reindex(
        index=M_GRID, columns=THETA_GRID, fill_value=0)
    prop = tab.to_numpy() / len(post)
    ax.imshow(prop, origin="lower", cmap="Reds", aspect="auto", vmin=0, vmax=max(prop.max(), 1e-9))
    ax.set_xticks(range(len(THETA_GRID)))
    ax.set_xticklabels([f"{t:g}" for t in THETA_GRID])
    ax.set_yticks(range(len(M_GRID)))
    ax.set_yticklabels([f"{m:g}" for m in M_GRID])
    ax.set_xticks(np.arange(-0.5, len(THETA_GRID)), minor=True)
    ax.set_yticks(np.arange(-0.5, len(M_GRID)), minor=True)
    ax.grid(which="minor", color="lightgrey", ls=":")
    ax.tick_params(which="minor", length=0)
    r, c = np.unravel_index(np.argmax(prop), prop.shape)
    ax.text(c, r, f"{100 * prop[r, c]:.1f}%", color="white", ha="center", va="center")
    ax.plot(np.argmin(abs(THETA_GRID - true_theta)), np.argmin(abs(M_GRID - true_m)),
            "ko", ms=10, label="true value")
    ax.set_xlabel(r"Conformity exponent $\theta$")
    ax.set_ylabel(r"Migration rate $\it{m}$")
    ax.set_title(label, loc="left", fontsize=12)


def predictive_panel(ax, last_fst, ref_fst, label):
    x, y = r_density(last_fst)
    ax.plot(x, y, color="#CD0000", lw=2)
    ax.axvline(ref_fst, ls="--", lw=2, color="black")
    ax.set_xlabel(r"CF$_{ST}$")
    ax.set_ylabel("Density")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_title(label, loc="left", fontsize=12)


def contrast_panel(ax, up, down, col, label):
    for diff, c, txt, xpos in ((up, col[5], "+10% \n migration", 0.2),
                               (down, col[4], "-10% \n migration", 0.8)):
        if diff is None:
            continue
        x, y = r_density(diff)
        ax.fill(x, y, color=alpha(c, 0.2), ec="black", lw=0.8)
        ax.text(xpos, 0.85, txt, color=c, transform=ax.transAxes, ha="center", fontsize=9)
    ax.axvline(0, ls="--", lw=2, color="black")
    ax.set_yticks([])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.set_xlabel(r"M -> CF$_{ST}$")
    ax.set_title(label, loc="left", fontsize=12)


def plot_figure5(R, path):
    import matplotlib.pyplot as plt
    col = color_ramp(SET1, N_GROUPS)
    fig, axes = plt.subplots(2, 3, figsize=(18 / 2.54 * 1.4, 15 / 2.54 * 1.4))
    joint_posterior_panel(axes[0, 0], R["post_un"], 1.0, 0.3, "a")
    predictive_panel(axes[0, 1], R["last_fst_un"], R["ref_un"][0][-1], "b")
    contrast_panel(axes[0, 2], R["diff_un_up"], R["diff_un_down"], col, "c")
    joint_posterior_panel(axes[1, 0], R["post_c"], 2.0, 0.1, "d")
    predictive_panel(axes[1, 1], R["last_fst_c"], R["ref_c"][0][-1], "e")
    contrast_panel(axes[1, 2], R["diff_c_up"], R["diff_c_down"], col, "f")
    fig.tight_layout()
    fig.savefig(path, dpi=500)
    plt.close(fig)


# --------------------------------------------------------------------------- #
def main(argv=None):
    import matplotlib
    matplotlib.use("Agg")
    p = argparse.ArgumentParser(prog="miras paper abc", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--n-comb", type=int, default=100_000, help="ABC simulations per analysis")
    p.add_argument("--n-accept", type=int, default=1000, help="closest simulations kept as posterior")
    p.add_argument("--post-pred-n", type=int, default=100, help="posterior predictive simulations")
    p.add_argument("--n-steps", type=int, default=100)
    p.add_argument("--n-burn-in", type=int, default=1000)
    p.add_argument("--cores", type=int, default=os.cpu_count())
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--outdir", default="output")
    p.add_argument("--reuse", action="store_true", help="load cached results if present")
    p.add_argument("--legacy-aging", action="store_true", help="replicate the R ageing quirk")
    p.add_argument("--quick", action="store_true", help="tiny smoke-test run")
    p.add_argument("--track", action="store_true", help="record the run with daftar")
    args = p.parse_args(argv)
    if args.quick:
        args.n_comb, args.n_accept, args.post_pred_n = 60, 20, 6
        args.n_steps, args.n_burn_in = 60, 100

    os.makedirs(args.outdir, exist_ok=True)
    cache = os.path.join(args.outdir, "abc_results.pkl")
    if args.reuse and os.path.exists(cache):
        with open(cache, "rb") as fh:
            R = pickle.load(fh)
        plot_figure5(R, os.path.join(args.outdir, "abc_result.png"))
        return

    rng = np.random.default_rng(args.seed)
    legacy = args.legacy_aging
    sim = dict(N=3000, n_groups=N_GROUPS, n_steps=args.n_steps, n_burn_in=args.n_burn_in,
               n_mod=30, r_dist=0.0, legacy_aging=legacy)
    R = {}

    with Pool(args.cores) as pool:
        # --- Unbiased transmission reference population ---
        print("Reference data: unbiased transmission (m = 0.3, theta = 1)")
        R["ref_un"] = mig_abm(np.random.default_rng(args.seed + 1),
                              m_const=0.3, mu=0.05, theta=1.0, **sim)
        jobs_un = make_jobs(rng, args.n_comb, args.n_steps, args.n_burn_in)
        print(f"ABC: {args.n_comb} simulations")
        diff_un = run_abc(pool, jobs_un, R["ref_un"], args.seed + 2, legacy)

        # --- Conformist transmission reference population ---
        print("Reference data: conformist transmission (m = 0.1, theta = 2)")
        R["ref_c"] = mig_abm(np.random.default_rng(args.seed + 3),
                             m_const=0.1, mu=0.1, theta=2.0, **sim)
        jobs_c = make_jobs(rng, args.n_comb, args.n_steps, args.n_burn_in)
        print(f"ABC: {args.n_comb} simulations")
        diff_c = run_abc(pool, jobs_c, R["ref_c"], args.seed + 4, legacy)

        with open(os.path.join(args.outdir, "abc_raw.pkl"), "wb") as fh:
            pickle.dump(dict(jobs_un=jobs_un, diff_un=diff_un, ref_un=R["ref_un"],
                             jobs_c=jobs_c, diff_c=diff_c, ref_c=R["ref_c"]), fh)

        # --- Rejection step: joint posteriors ---
        R["post_un"] = rejection(jobs_un, diff_un, args.n_accept)
        R["post_c"] = rejection(jobs_c, diff_c, args.n_accept)

        # --- Posterior predictions (Fst in the last year) ---
        n = args.post_pred_n
        print("Posterior predictions ...")
        R["last_fst_un"] = predict(pool, first_n(R["post_un"], n, "unbiased"), args.seed + 5, legacy)
        R["last_fst_c"] = predict(pool, first_n(R["post_c"], n, "conformist"), args.seed + 6, legacy)

        # --- Contrasts: effect of changing migration by 10 percentage points ---
        print("Contrasts ...")
        pu = R["post_un"]
        post_02 = pu[np.isclose(pu["m_const"], 0.2)]
        post_03 = pu[np.isclose(pu["m_const"], 0.3)]
        post_01 = shift_m(post_02, -0.1)
        f01 = predict(pool, first_n(post_01, n, "unbiased m=0.1"), args.seed + 7, legacy)
        f02 = predict(pool, first_n(post_02, n, "unbiased m=0.2"), args.seed + 8, legacy)
        f03 = predict(pool, first_n(post_03, n, "unbiased m=0.3"), args.seed + 9, legacy)

        post_02_c = shift_m(R["post_c"], 0.1)
        post_03_c = shift_m(post_02_c, 0.1)
        fc01 = R["last_fst_c"]
        fc02 = predict(pool, first_n(post_02_c, n, "conformist m+0.1"), args.seed + 10, legacy)
        fc03 = predict(pool, first_n(post_03_c, n, "conformist m+0.2"), args.seed + 11, legacy)

    sub = lambda a, b: None if a is None or b is None else a - b
    R["diff_un_up"], R["diff_un_down"] = sub(f03, f02), sub(f01, f02)
    R["diff_c_up"], R["diff_c_down"] = sub(fc03, fc02), sub(fc01, fc02)

    with open(cache, "wb") as fh:
        pickle.dump(R, fh)
    for name, post in (("unbiased", R["post_un"]), ("conformist", R["post_c"])):
        print(f"\nJoint posterior ({name}):")
        print(pd.crosstab(post["m_const"], post["theta"]))
    path = os.path.join(args.outdir, "abc_result.png")
    plot_figure5(R, path)
    # provenance: recorded after the fact, so wall-clock time is not meaningful
    with tracked("paper-abc", params=vars(args), seed=args.seed, enabled=args.track) as run:
        for name, post in (("unbiased", R["post_un"]), ("conformist", R["post_c"])):
            run.log_result(f"{name}.posterior_mean_m", float(post["m_const"].mean()))
            run.log_result(f"{name}.posterior_mean_theta", float(post["theta"].mean()))
        run.add_output(path)
        run.add_output(cache)
    print(f"\nFigure written to {path}")


if __name__ == "__main__":
    main()
