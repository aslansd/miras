"""
Deffner, D., Fedorova, N., Andrews, J. & McElreath, R.
Bridging theory and data: A computational workflow for cultural evolution
Agent-based simulation model (R original by D. Deffner, ConDiv_ABM.R; ported to miras)

Simulates the agent-based model combining migration and conformity over a grid
of conformity exponents (theta) and migration rates (m) and plots Fig. 3.

The full sweep (22 theta x 21 m values x 100 simulations x 1300 years) is
heavy: ~46,000 simulations of a few seconds each. Use --cores and/or reduce
--nsim for a lighter run; --quick gives a small smoke test.

Usage:
    miras paper abm --cores 16                # full sweep + figure
    miras paper abm --plot-only               # re-plot from saved results

An interrupted sweep (Ctrl-C) is checkpointed every two minutes; running the
same command again resumes it, with results identical to an uninterrupted run.
"""
import argparse
import os

import numpy as np

from ._model import paper_model
from ._plot import SET1, alpha, shade_density, spawn_seeds
from ._runner import Checkpoint, Progress, interrupted_message, make_pool
from ..provenance import tracked

MU = 0.05            # innovation rate (other constants: see paper_model)

# Parameter sweep, same order as R's expand.grid (theta varies fastest)
THETAS = np.round(np.arange(0.8, 5.0 + 1e-9, 0.2), 10)
MIGS = np.round(np.arange(0.0, 0.4 + 1e-9, 0.02), 10)
SWEEP_THETA = np.tile(THETAS, len(MIGS))
SWEEP_M = np.repeat(MIGS, len(THETAS))


def combo(theta, m):
    """Index of a (theta, m) combination. (R used hard-coded indices because
    `seq$theta == 1.2` failed on floating point; this uses a tolerance.)"""
    hit = np.flatnonzero(np.isclose(SWEEP_THETA, theta) & np.isclose(SWEEP_M, m))
    if hit.size != 1:
        raise KeyError(f"theta={theta}, m={m} not in sweep")
    return int(hit[0])


def _job(args):
    k, c, n_steps, seed, burn_in, legacy = args
    model = paper_model(theta=SWEEP_THETA[c], m=SWEEP_M[c], mu=MU, legacy_aging=legacy)
    return k, model.simulate(n_steps, burn_in=burn_in, seed=seed, record=("fst",)).series["fst"]


def run_sweep(nsim, n_steps, cores, seed, burn_in, legacy, checkpoint=None):
    """All (theta, m) combinations x nsim simulations. Simulation k belongs to
    combination k // nsim and has a seed fixed by k, so a resumed sweep gives
    the same numbers as an uninterrupted one."""
    n_combo = len(SWEEP_THETA)
    n_jobs = n_combo * nsim
    seeds = spawn_seeds(seed, n_jobs)
    result = np.full((n_combo, nsim, n_steps), np.nan, dtype=np.float32)
    done = np.zeros(n_jobs, dtype=bool)
    state = checkpoint.load() if checkpoint else None
    if state is not None:
        result, done = state["fst"], state["done"].astype(bool)
        print(f"  resuming: {int(done.sum())}/{n_jobs} simulations already done", flush=True)
    jobs = [(k, k // nsim, n_steps, seeds[k], burn_in, legacy) for k in np.flatnonzero(~done)]
    progress = Progress(n_jobs, already=int(done.sum()))
    try:
        with make_pool(cores) as pool:
            for k, fst in pool.imap_unordered(_job, jobs, chunksize=4):
                result[k // nsim, k % nsim] = fst
                done[k] = True
                progress.tick()
                if checkpoint and checkpoint.due():
                    checkpoint.save(fst=result, done=done)
    except KeyboardInterrupt:
        if checkpoint:
            checkpoint.save(fst=result, done=done)
            print(interrupted_message(int(done.sum()), n_jobs, checkpoint.path))
        raise
    if checkpoint:
        checkpoint.remove()
    return result


def plot_figure3(result, path, illustration=None):
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    nsim = result.shape[1]
    col = SET1
    fig = plt.figure(figsize=(13, 4))
    gs = GridSpec(1, 4, width_ratios=[2, 2, 3, 2], figure=fig, wspace=0.35)

    # a) model illustration (image not included in the repository)
    ax = fig.add_subplot(gs[0])
    ax.axis("off")
    if illustration and os.path.exists(illustration):
        ax.imshow(plt.imread(illustration))
    else:
        ax.text(0.5, 0.5, "ModelIllustration.png\n(not included in repo)",
                ha="center", va="center", color="grey")
    ax.set_title("Model Illustration", fontsize=10)
    ax.text(0, 1.08, "a", transform=ax.transAxes, fontsize=12)

    # b) simulation dynamics
    ax = fig.add_subplot(gs[1])
    t_plot = min(100, result.shape[2])
    x = np.arange(1, t_plot + 1)
    curves = [((1.0, 0.0), col[0], (70, 0.3), "no migration \n unbiased"),
              ((1.4, 0.0), col[1], (70, 0.95), "no migration \n weak conformity"),
              ((1.4, 0.2), col[2], (20, 0.01), "migration \n weak conformity"),
              ((2.0, 0.2), col[3], (70, 0.65), "migration \n strong conformity")]
    for (theta, m), c, (tx, ty), label in curves:
        for i in range(nsim):
            ax.plot(x, result[combo(theta, m), i, :t_plot], color=alpha(c, 0.3), lw=0.8)
        ax.text(tx, ty, label, color=c, ha="center", va="center", fontsize=9)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Simulation year")
    ax.set_ylabel(r"Cultural F$_{ST}$")
    ax.set_title("Simulation Dynamics", fontsize=10)
    ax.text(-0.15, 1.08, "b", transform=ax.transAxes, fontsize=12)

    # Remove first 100 years, mean Fst per parameter combination
    burn = min(100, result.shape[2] - 1)
    res = result[:, :, burn:]
    overall = res.mean(axis=2).mean(axis=1)

    # c) heat map for theta <= 3
    ax = fig.add_subplot(gs[2])
    th_sel = THETAS[THETAS <= 3 + 1e-9]
    z = np.array([[overall[combo(th, m)] for m in MIGS] for th in th_sel])
    im = ax.imshow(z.T, origin="lower", aspect="auto", cmap="YlOrRd",
                   vmin=0, vmax=np.nanmax(z), extent=[0.5, len(th_sel) + 0.5, 0.5, len(MIGS) + 0.5])
    ax.set_xticks(range(1, len(th_sel) + 1))
    ax.set_xticklabels([f"{t:g}" for t in th_sel], rotation=90, fontsize=8)
    ax.set_yticks(range(1, len(MIGS) + 1, 5))
    ax.set_yticklabels([f"{m:g}" for m in MIGS[::5]])
    ax.axvline(1.5, color="k", lw=3)
    ax.axvline(2.5, color="k", lw=3)
    ax.text(2, 11, "Unbiased transmission", rotation=90, ha="center", va="center", fontsize=10)
    ax.text(1, 11, "Anti-conformity", rotation=90, ha="center", va="center", fontsize=10)
    ax.text(7.5, 11, "Conformity", ha="center", va="center", fontsize=12)
    ax.set_xlabel(r"Conformity exponent  $\it{\theta}$")
    ax.set_ylabel(r"Migration rate $\it{m}$")
    ax.set_title(r"Cultural F$_{ST}$ per parameter combination", fontsize=10)
    ax.text(-0.08, 1.08, "c", transform=ax.transAxes, fontsize=12)
    fig.colorbar(im, ax=ax, fraction=0.05, pad=0.02)

    # d) causal effect of m = 0.1 -> 0.2 for three theta values
    ax = fig.add_subplot(gs[3])
    axes = [ax, ax.twinx(), ax.twinx()]           # R overlays plots with different ylims
    ylims = [200, 30, 30]
    for a_, theta, c, yl in zip(axes, (1.0, 1.4, 2.0), (col[0], col[1], col[3]), ylims):
        low = res[combo(theta, 0.1)].ravel()
        high = res[combo(theta, 0.2)].ravel()
        shade_density(a_, high - low, c)
        a_.set_ylim(0, yl)
        a_.set_yticks([])
        for s in ("top", "right", "left"):
            a_.spines[s].set_visible(False)
    ax.set_xlim(-0.6, 0)
    ax.axvline(0, ls="--", color="lightgrey")
    handles = [plt.Line2D([], [], color=c, lw=6) for c in (col[0], col[1], col[3])]
    ax.legend(handles, ["1", "1.4", "2"], title=r"Conformity exp. $\it{\theta}$",
              loc="upper center", frameon=False)
    ax.set_xlabel(r"M -> CF$_{ST}$")
    ax.set_title("Causal Effects", fontsize=10)
    ax.text(-0.05, 1.08, "d", transform=ax.transAxes, fontsize=12)

    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def main(argv=None):
    import matplotlib
    matplotlib.use("Agg")
    p = argparse.ArgumentParser(prog="miras paper abm", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--nsim", type=int, default=100, help="simulations per parameter combination")
    p.add_argument("--n-steps", type=int, default=300, help="years after burn-in")
    p.add_argument("--n-burn-in", type=int, default=1000)
    p.add_argument("--cores", type=int, default=os.cpu_count())
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--outdir", default="output")
    p.add_argument("--illustration", default="ModelIllustration.png")
    p.add_argument("--plot-only", action="store_true", help="re-plot from saved results")
    p.add_argument("--legacy-aging", action="store_true",
                   help="replicate the R ageing quirk (see README)")
    p.add_argument("--quick", action="store_true", help="tiny smoke-test run")
    p.add_argument("--fresh", action="store_true",
                   help="ignore a checkpoint from an interrupted run and start over")
    p.add_argument("--track", action="store_true", help="record the run with daftar")
    args = p.parse_args(argv)
    if args.quick:
        args.nsim, args.n_steps, args.n_burn_in = 2, 120, 100

    os.makedirs(args.outdir, exist_ok=True)
    res_path = os.path.join(args.outdir, "abm_results.npz")
    with tracked("paper-abm", params=vars(args), seed=args.seed, enabled=args.track) as run:
        if args.plot_only:
            result = np.load(res_path)["fst"]
        else:
            print(f"Running {len(SWEEP_THETA)} parameter combinations x {args.nsim} simulations "
                  f"on {args.cores} cores ...")
            from .. import __version__
            ckpt = Checkpoint(os.path.join(args.outdir, "abm_checkpoint.npz"),
                              {"workflow": "abm", "nsim": args.nsim, "n_steps": args.n_steps,
                               "burn_in": args.n_burn_in, "seed": args.seed,
                               "legacy_aging": args.legacy_aging, "version": __version__})
            if args.fresh:
                ckpt.remove()
            result = run_sweep(args.nsim, args.n_steps, args.cores, args.seed,
                               args.n_burn_in, args.legacy_aging, checkpoint=ckpt)
            np.savez_compressed(res_path, fst=result, theta=SWEEP_THETA, m=SWEEP_M)
            run.add_output(res_path)
            print(f"Saved results to {res_path}")

        fig_path = os.path.join(args.outdir, "Abstract_ABM.pdf")
        plot_figure3(result, fig_path, args.illustration)
        run.add_output(fig_path)
        run.log_result("mean_fst", float(np.nanmean(result)))
    print(f"Figure written to {fig_path}")


if __name__ == "__main__":
    main()
