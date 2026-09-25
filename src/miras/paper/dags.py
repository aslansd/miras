"""
Deffner, D., Fedorova, N., Andrews, J. & McElreath, R.
Bridging theory and data: A computational workflow for cultural evolution
Simulation of synthetic data and power analysis
(R original by J. Andrews and D. Deffner, DAGstoData.R; ported to miras)

Simulates synthetic data for 30 countries from the DAG in Fig. 2b
(A -> C, A -> M, M -> D, C -> D), runs a power analysis varying unexplained
variance (sigma) and the effect size of M on D, and computes the causal effect
of M on D (marginalising over C) from a Bayesian model fitted with Stan.

Usage:
    miras paper dags [--outdir DAGstoData_Plots] [--seed 1] [--skip-stan] [--track]
"""
import argparse
import os

import numpy as np


import matplotlib.pyplot as plt

from ._plot import SET1, shade_density, clean_density_axis
from ..provenance import tracked

# Parameters
SIGMA = np.linspace(0.01, 3, 10)       # unexplained variance in the diversity metric
BMD = 10.0 ** -np.arange(10)           # magnitude of the effect of migration on diversity
BCD = 1.0                              # effect of conformity on diversity
BAM = 1.0                              # effect of age on migration
BAC = 1.0                              # effect of age on conformity
N_COUNTRIES = 30


def sim_dat(rng, bmd, sigma, n=N_COUNTRIES):
    """Simulate A (age), C (conformity), M (migration) and D (diversity)."""
    A = rng.normal(0, 1, n)
    C = rng.normal(A * BAC, 1)
    M = rng.normal(A * BAM, 1)
    D = rng.normal(M * bmd + C * BCD, sigma)
    return {"A": A, "C": C, "M": M, "D": D}


def ols_coef_M(d):
    """Least-squares estimate of the M coefficient in lm(D ~ M + C)."""
    X = np.column_stack([np.ones_like(d["M"]), d["M"], d["C"]])
    beta, *_ = np.linalg.lstsq(X, d["D"], rcond=None)
    return beta[1]


def power_analysis(rng, n_rep=200):
    """Mean log relative error log|bmd_est / bmd_true| for every (bmd, sigma)."""
    err = np.full((len(BMD), len(SIGMA)), np.nan)
    for j, sigma in enumerate(SIGMA):
        for i, bmd in enumerate(BMD):
            # NOTE (fix vs. R original): the R loop fitted `data[[i]]` (the
            # sweep index) instead of `data[[j]]`, so every "replicate" reused
            # the same dataset. Here each of the n_rep datasets is fitted.
            est = np.array([ols_coef_M(sim_dat(rng, bmd, sigma)) for _ in range(n_rep)])
            err[i, j] = np.mean(np.log(np.abs(est / bmd)))
    return err


def plot_power(err, path):
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(err, origin="lower", aspect="auto", cmap="YlOrRd",
                   extent=[SIGMA[0], SIGMA[-1], -0.5, 9.5])
    ax.set_xlabel("Unexplained variance (Sigma)")
    ax.set_ylabel("Effect of migration [10^-(bmd)]")
    ax.set_yticks(range(10))
    ax.set_title("Error [log(bmd_est / bmd_real)]")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def causal_effect(rng, iter_warmup=1500, iter_sampling=1500, chains=4):
    """Fit D ~ a + bmd*M + bcd*C with Stan, then simulate interventions M=+1 vs
    M=-1, averaging over the empirical distribution of C."""
    from ..inference import stan

    dat = sim_dat(rng, 1.0, 1.0)
    fit = stan.sample(
        "dags_to_data",
        {"N": N_COUNTRIES, "D": dat["D"].tolist(), "M": dat["M"].tolist(), "C": dat["C"].tolist()},
        chains=chains, iter_warmup=iter_warmup, iter_sampling=iter_sampling,
        seed=int(rng.integers(1, 2**31 - 1)), show_progress=False,
    )
    s = {k: fit.stan_variable(k) for k in ("a", "bmd", "bcd", "sigma")}
    n = s["sigma"].size
    Cs = rng.choice(dat["C"], n, replace=True)     # sample C from its "empirical" distribution
    mu_hi = s["a"] + s["bcd"] * Cs + s["bmd"] * 1
    mu_lo = s["a"] + s["bcd"] * Cs + s["bmd"] * (-1)
    return rng.normal(mu_hi, s["sigma"]) - rng.normal(mu_lo, s["sigma"])


def plot_effect(effect, path):
    fig, ax = plt.subplots(figsize=(4, 4))
    shade_density(ax, effect, SET1[0])
    ax.set_xlim(-4, 8)
    ax.set_ylim(0, 0.4)
    clean_density_axis(ax)
    ax.set_xlabel("M -> D", fontsize=12)
    ax.set_title("Causal effect of M on D\n(marginalizing over C)", fontsize=10)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main(argv=None):
    import matplotlib
    matplotlib.use("Agg")
    p = argparse.ArgumentParser(prog="miras paper dags", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--outdir", default="DAGstoData_Plots")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--n-rep", type=int, default=200, help="datasets per parameter combination")
    p.add_argument("--skip-stan", action="store_true", help="only run the power analysis")
    p.add_argument("--track", action="store_true", help="record the run with daftar")
    args = p.parse_args(argv)

    os.makedirs(args.outdir, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    with tracked("paper-dags", params=vars(args), seed=args.seed, enabled=args.track) as run:
        print("Power analysis ...")
        err = power_analysis(rng, args.n_rep)
        path = os.path.join(args.outdir, "DAGstoDataPower.pdf")
        plot_power(err, path)
        run.add_output(path)

        if not args.skip_stan:
            print("Fitting Stan model for the causal effect ...")
            effect = causal_effect(rng)
            path = os.path.join(args.outdir, "DAGstoDataEffect.pdf")
            plot_effect(effect, path)
            run.add_output(path)
            run.log_result("causal_effect_mean", float(effect.mean()))
            print(f"Causal effect of M (+1 vs -1) on D: mean {effect.mean():.2f}, "
                  f"90% interval {np.quantile(effect, [0.05, 0.95]).round(2)}")
    print(f"Plots written to {args.outdir}/")


if __name__ == "__main__":
    main()
