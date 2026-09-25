"""
Deffner, D., Fedorova, N., Andrews, J. & McElreath, R.
Bridging theory and data: A computational workflow for cultural evolution
Longitudinal transmission analysis
(R original by D. Deffner, ConDiv_LongitudinalTransmission.R; ported to miras)

1) Simulates longitudinal data on cultural traits and social networks for
   hypothetical participants, using real age-specific migration rates from the
   Netherlands (beta_df.csv).
2) Fits the multilevel time-series transmission model Longitudinal_Conf.stan
   (shipped with miras) with CmdStan via cmdstanpy.
3) Pushes posterior draws back through the ABM to compute the causal effect of
   +/-5% migration on cultural Fst.
4) Plots Fig. 4.

Each stage caches its output in --outdir; use --reuse to skip stages whose
output already exists (e.g. to re-plot without refitting).

Usage:
    miras paper longitudinal --cores 8
    miras paper longitudinal --reuse                  # re-plot from cache
    miras paper longitudinal --identify 6             # Stan identifiability report

--identify N simulates N datasets at known (mu, theta), fits the Stan model to
each and reports with miras.analyze whether the design recovers them.
"""
import argparse
import json
import os
import pickle
import time
from multiprocessing import Pool

import numpy as np

from ._data import age_migration_nl as load_age_migration
from ._model import paper_model
from ._plot import (SET1, alpha, color_ramp, hpdi, inv_logit, shade_density,
                    clean_density_axis, spawn_seeds)
from ..engine import migration_vector
from ..provenance import tracked
from ..stats import cultural_fst

# --------------------------------------------------------------------------- #
# Parameters of the data-generating simulation
# --------------------------------------------------------------------------- #
DATA_PARAMS = dict(
    N=3000,          # number of agents
    n_groups=30,     # number of groups
    n_steps=30,      # number of recorded years
    n_burn_in=1000,  # years to reach equilibrium age structure
    n_skip=100,      # years before we record choices for analysis
    n_mod=30,        # number of role models
    m_NL=True,       # True: real NL migration rates; False: constant m_const
    m_const=0.01,
    mu=0.1,          # innovation rate
    f=3.0,           # conformity exponent (true theta)
    size_grid=50,
    r_dist=0.0,      # effect of distance on migration
    r_learn=0.0,     # everyone updates every year
    r_mort=0.001,
    n_record=500,    # number of participants we collect data from
)

# Parameters for the posterior simulations (as in the R script)
SIM_PARAMS = dict(
    N=3000, n_groups=30, n_burn_in=1000, max_age=90, n_mod=30,
    size_grid=50, r_dist=0.0, r_learn=0.03, r_mort=0.001,
)


# --------------------------------------------------------------------------- #
# 1) Simulate longitudinal data
# --------------------------------------------------------------------------- #
def simulate_data(rng, age_mig_NL, P, legacy_aging=False):
    """Run the model and record, for n_record tracked participants, their
    variant, age, group and the variants of their sampled role models each year."""
    N, n_mod, n_rec, n_steps = P["N"], P["n_mod"], P["n_record"], P["n_steps"]
    max_age = len(age_mig_NL)
    model = paper_model(theta=P["f"], mu=P["mu"], r_learn=P["r_learn"], r_mort=P["r_mort"],
                        max_age=max_age, n_groups=P["n_groups"], group_size=N // P["n_groups"],
                        n_models=n_mod, size_grid=P["size_grid"], r_dist=P["r_dist"],
                        include_self=True, legacy_aging=legacy_aging)
    pop = model.new_population(rng)
    demography, rule = model.demography, model.learning
    m_vec = migration_vector(age_mig_NL if P["m_NL"] else P["m_const"], max_age)

    ids = rng.permutation(N)          # 0-based participant ids; ids < n_record are tracked
    next_id = N
    start = P["n_burn_in"] + P["n_skip"]

    dat_trait = np.full((n_rec, n_steps), np.nan)
    dat_models = np.full((n_rec, n_steps, n_mod), np.nan)
    dat_age = np.full((n_rec, n_steps), np.nan)
    dat_group = np.full((n_rec, n_steps), np.nan)
    diversity = np.zeros(n_steps)
    everyone = np.arange(N)

    for t in range(start + n_steps):
        if t % 100 == 0:
            print(f"  year {t}/{start + n_steps}", flush=True)
        babies = demography.step(pop)
        if t >= start and babies.size:       # newborns get new ids once recording starts
            ids[babies] = next_id + np.arange(babies.size)
            next_id += babies.size

        if t < P["n_burn_in"]:
            continue
        pop.migrate(m_vec)
        learners = demography.learners(pop)
        models = pop.sample_models(everyone, n_mod)   # every agent samples models ...
        if t >= start:                                # ... so we can record networks
            s = t - start
            tr = np.flatnonzero(ids < n_rec)
            dat_models[ids[tr], s, :] = pop.traits[models[tr]]
        # learners consider their own variant alongside their models' (include_self)
        pop.update(learners, rule.choose(pop, learners, models[learners]), P["mu"])

        if t >= start:
            diversity[s] = cultural_fst(pop.traits, pop.group)[0]
            tr = np.flatnonzero(ids < n_rec)
            dat_trait[ids[tr], s] = pop.traits[tr]
            dat_age[ids[tr], s] = pop.age[tr]
            dat_group[ids[tr], s] = pop.group[tr]

    return dict(trait=dat_trait, models=dat_models, age=dat_age, group=dat_group,
                diversity=diversity)


def build_stan_data(d, n_mod):
    """Restructure the simulated panel into the long format the Stan model
    expects. The first recorded year of each participant is dropped (no
    previous trait to compare with), as in the R code."""
    n_rec, n_steps = d["trait"].shape
    rows = dict(choices=[], innovate=[], migrate=[], id=[], age=[], group=[],
                frequencies=[], N_alt=[])
    for i in range(n_rec):
        for t in range(1, n_steps):
            if np.isnan(d["trait"][i, t]):
                continue                                   # participant has died
            choice = int(d["trait"][i, t])
            all_traits = [int(x) for x in d["models"][i, t]] + [int(d["trait"][i, t - 1])]
            available = list(dict.fromkeys(all_traits))    # unique, order preserved
            n = [all_traits.count(a) for a in available]
            freq = np.full(n_mod + 1, -10.0)
            freq[: len(n)] = n
            if choice in available:
                innov, ch = 0, available.index(choice) + 1  # Stan is 1-based
            else:
                innov, ch = 1, -10
            rows["choices"].append(ch)
            rows["innovate"].append(innov)
            # NOTE (fix vs. R original): R compared against a group vector
            # whose first-year entry was never filled (-10), so every
            # participant's first analysed year was coded as a migration.
            rows["migrate"].append(int(d["group"][i, t - 1] != d["group"][i, t]))
            rows["id"].append(i)
            rows["age"].append(int(d["age"][i, t]))
            rows["group"].append(int(d["group"][i, t]))
            rows["frequencies"].append(freq)
            rows["N_alt"].append(len(n))

    def reindex(x):   # consecutive 1-based indices in order of first appearance
        uniq = list(dict.fromkeys(x))
        lookup = {u: k + 1 for k, u in enumerate(uniq)}
        return [lookup[v] for v in x], len(uniq)

    sd = {k: rows[k] for k in ("choices", "innovate", "migrate", "age", "N_alt")}
    sd["id"], sd["N_id"] = reindex(rows["id"])
    sd["group"], sd["N_groups"] = reindex(rows["group"])
    sd["frequencies"] = np.array(rows["frequencies"]).tolist()
    sd["N"] = len(sd["choices"])
    sd["N_partners"] = n_mod
    sd["Max_age"] = int(max(sd["age"]))
    return sd


# --------------------------------------------------------------------------- #
# 2) Fit Stan model
# --------------------------------------------------------------------------- #
def fit_model(stan_data, seed, cores, outdir, iter_warmup=1500, iter_sampling=1500, chains=4,
              show_progress=True):
    from ..inference import stan
    os.makedirs(outdir, exist_ok=True)
    data_file = os.path.join(outdir, "longitudinal_stan_data.json")
    with open(data_file, "w") as fh:
        json.dump(stan_data, fh)
    fit = stan.sample("Longitudinal_Conf", data_file, seed=seed, chains=chains,
                      iter_warmup=iter_warmup, iter_sampling=iter_sampling,
                      adapt_delta=0.8, max_treedepth=13, show_progress=show_progress,
                      output_dir=os.path.join(outdir, "stan_output"))
    diag = stan.convergence(fit)
    print(f"  max R-hat = {diag['max_rhat']:.3f}, divergent transitions = {diag['divergences']}")
    draws = {k: fit.stan_variable(k) for k in ("logit_mu", "log_theta", "age_effects")}
    draws["_diagnostics"] = np.array([diag["max_rhat"], diag["divergences"]])
    return draws


# --------------------------------------------------------------------------- #
# 3) Simulate with posterior estimates -> causal effects
# --------------------------------------------------------------------------- #
def _post_job(args):
    theta, mu, m, seed, n_steps, params = args
    model = paper_model(theta=theta, m=m, mu=mu, r_learn=params["r_learn"],
                        r_mort=params["r_mort"], max_age=params["max_age"],
                        legacy_aging=params.get("legacy_aging", False))
    return model.simulate(n_steps, burn_in=params["n_burn_in"], seed=seed,
                          record=("fst",)).series["fst"]


def posterior_simulations(draws, n_per_cond, n_steps, cores, seed, params):
    rng = np.random.default_rng(seed)
    n_draws = draws["log_theta"].size
    sample = rng.choice(n_draws, 3 * n_per_cond, replace=n_draws < 3 * n_per_cond)
    m_in = np.repeat([0.0, 0.05, -0.05], n_per_cond)   # empirical, +5%, -5% migration
    jobs = []
    for k, (s, dm, r) in enumerate(zip(sample, m_in, spawn_seeds(seed + 1, len(sample)))):
        theta = float(np.exp(draws["log_theta"][s]))
        mu = float(inv_logit(draws["logit_mu"][s]))
        m = inv_logit(draws["age_effects"][s]) + dm
        jobs.append((theta, mu, m, r, n_steps, params))
    t0 = time.time()
    out = []
    with Pool(cores) as pool:
        for k, fst in enumerate(pool.imap(_post_job, jobs), 1):
            out.append(fst)
            if k % 10 == 0:
                print(f"  {k}/{len(jobs)} posterior simulations ({time.time() - t0:.0f}s)", flush=True)
    out = np.array(out)
    burn = min(100, n_steps - 1)
    split = lambda a: out[a * n_per_cond:(a + 1) * n_per_cond, burn:].ravel()
    return dict(emp=split(0), high=split(1), low=split(2))


# --------------------------------------------------------------------------- #
# 4) Figure 4
# --------------------------------------------------------------------------- #
def plot_figure4(d, draws, sims, age_mig_NL, P, max_age_data, path):
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    col = color_ramp(SET1, P["n_groups"])    # R reassigns col.pal to a 30-colour ramp here
    fig = plt.figure(figsize=(12, 4))
    gs = GridSpec(1, 5, width_ratios=[2, 1, 1, 2, 2], figure=fig, wspace=0.3)

    # a) time series of participants and their groups
    ax = fig.add_subplot(gs[0])
    n_steps = d["trait"].shape[1]
    for i in range(min(100, d["trait"].shape[0])):
        alive = np.flatnonzero(~np.isnan(d["trait"][i]))
        if alive.size == 0:
            continue
        T = alive.max() + 1
        x = np.arange(1, T + 1)
        ax.plot(x, np.full(T, i + 1), color=alpha("black", 0.3), lw=0.8)
        g = d["group"][i, :T].astype(int)
        ax.scatter(x, np.full(T, i + 1), s=4, c=[alpha(col[k], 0.5) for k in g])
    ax.set_xlim(1, n_steps)
    ax.set_ylim(1, 100)
    ax.set_xlabel("Year")
    ax.set_ylabel("Participant ID")
    ax.text(-0.12, 1.05, "a", transform=ax.transAxes, fontsize=12)

    # b) innovation rate
    ax = fig.add_subplot(gs[1])
    shade_density(ax, inv_logit(draws["logit_mu"]), col[0])
    ax.axvline(P["mu"], ls="--", color="black", lw=2)
    clean_density_axis(ax)
    ax.set_xlabel(r"Innovation rate $\it{\mu}$")
    ax.text(-0.1, 1.05, "b", transform=ax.transAxes, fontsize=12)

    # conformity exponent
    ax = fig.add_subplot(gs[2])
    shade_density(ax, np.exp(draws["log_theta"]), col[0])
    ax.axvline(P["f"], ls="--", color="black", lw=2)
    clean_density_axis(ax)
    ax.set_xlabel(r"Conformity exp. $\it{\theta}$")

    # c) age-specific migration rates
    ax = fig.add_subplot(gs[3])
    MA = max_age_data
    ages = np.arange(1, MA + 1)
    ae = draws["age_effects"]
    for prob, a in ((0.9, 0.9), (1.0, 0.2)):
        lo, hi = np.array([hpdi(ae[:, k], prob) for k in range(MA)]).T
        ax.fill_between(ages, inv_logit(lo), inv_logit(hi), color=alpha(col[0], a), lw=0)
    # NOTE: R plotted age_mig_NL[2:MA] at x = 1..MA-1 (shifted by one year);
    # here the true rate for age a is drawn at age a.
    ax.plot(ages, age_mig_NL[:MA], "k--", lw=2)
    ax.set_ylim(0, 0.8)
    ax.set_xlabel("Age")
    ax.set_ylabel(r"Migration rate $\it{m}$")
    ax.text(-0.12, 1.05, "c", transform=ax.transAxes, fontsize=12)

    # d) causal effects of +/-5% migration
    ax = fig.add_subplot(gs[4])
    shade_density(ax, sims["high"] - sims["emp"], col[4])
    shade_density(ax, sims["low"] - sims["emp"], col[5])
    ax.set_xlim(-0.15, 0.15)
    ax.set_ylim(0, 30)
    clean_density_axis(ax)
    ax.axvline(0, ls="--", color="lightgrey")
    ax.text(-0.075, 26, "+5% \n migration", color=col[4], ha="center", fontsize=9)
    ax.text(0.075, 26, "-5% \n migration", color=col[5], ha="center", fontsize=9)
    ax.set_xlabel(r"M -> CF$_{ST}$")
    ax.text(-0.05, 1.05, "d", transform=ax.transAxes, fontsize=12)

    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# Identifiability of the longitudinal design, with Stan as the inference backend
# --------------------------------------------------------------------------- #
def stan_priors():
    """The Stan model's priors on (mu, theta) as miras priors:
    logit_mu ~ normal(0, 2), log_theta ~ normal(0, 1)."""
    from ..inference.priors import Normal
    return {"mu": Normal(0.0, 2.0, transform="logit"), "theta": Normal(0.0, 1.0, transform="log")}


DEFAULT_TRUTHS = [(mu, th) for th in (1.0, 2.0, 3.0) for mu in (0.05, 0.1, 0.2)]


def identify_stan(n_test, P, *, seed=1, iter_total=3000, cores=1, outdir="output",
                  truths=None, legacy_aging=False):
    """Simulate `n_test` longitudinal datasets at known (mu, theta), fit the
    Stan model to each, and report identifiability with miras.analyze."""
    from ..identify import analyze
    from ..inference.abc import Posterior

    truths = list(truths or DEFAULT_TRUTHS)
    truths = [truths[k % len(truths)] for k in range(n_test)]
    priors = stan_priors()
    age_mig_NL = load_age_migration()
    posts, truths_u = [], []
    for k, (mu, theta) in enumerate(truths):
        print(f"[{k + 1}/{n_test}] mu = {mu}, theta = {theta}: simulating and fitting ...", flush=True)
        rng = np.random.default_rng(seed + 1000 * k)
        d = simulate_data(rng, age_mig_NL, dict(P, mu=mu, f=theta), legacy_aging=legacy_aging)
        draws = fit_model(build_stan_data(d, P["n_mod"]), seed + k, cores,
                          os.path.join(outdir, f"identify_{k}"),
                          iter_warmup=iter_total // 2, iter_sampling=iter_total // 2,
                          show_progress=False)
        U = np.column_stack([draws["logit_mu"], draws["log_theta"]])
        posts.append(Posterior(priors, U, np.ones(len(U))))
        truths_u.append([np.log(mu / (1 - mu)), np.log(theta)])
    info = {"method": "stan", "design": f"{P['n_record']} participants x {P['n_steps']} years",
            "truths": [list(t) for t in truths]}
    return analyze(priors, np.array(truths_u), posts, info=info)


def main(argv=None):
    import matplotlib
    matplotlib.use("Agg")
    p = argparse.ArgumentParser(prog="miras paper longitudinal", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cores", type=int, default=os.cpu_count())
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--outdir", default="output")
    p.add_argument("--reuse", action="store_true", help="load cached stage outputs if present")
    p.add_argument("--n-post-sims", type=int, default=100, help="posterior simulations per condition")
    p.add_argument("--post-steps", type=int, default=300, help="years per posterior simulation")
    p.add_argument("--iter", type=int, default=3000, help="Stan iterations per chain (half warm-up)")
    p.add_argument("--identify", type=int, metavar="N", default=0,
                   help="instead of the figure, run a Stan identifiability report on N datasets")
    p.add_argument("--legacy-aging", action="store_true", help="replicate the R ageing quirk")
    p.add_argument("--quick", action="store_true", help="tiny smoke-test run")
    p.add_argument("--track", action="store_true", help="record the run with daftar")
    args = p.parse_args(argv)

    P = dict(DATA_PARAMS)
    sim_params = dict(SIM_PARAMS, legacy_aging=args.legacy_aging)
    if args.quick:
        P.update(n_burn_in=100, n_skip=20, n_steps=10, n_record=100)
        sim_params.update(n_burn_in=100)
        args.n_post_sims, args.post_steps, args.iter = 4, 120, 400

    os.makedirs(args.outdir, exist_ok=True)

    if args.identify:
        with tracked("paper-longitudinal-identify", params=vars(args), seed=args.seed,
                     enabled=args.track) as run:
            report = identify_stan(args.identify, P, seed=args.seed, iter_total=args.iter,
                                   cores=args.cores, outdir=args.outdir,
                                   legacy_aging=args.legacy_aging)
            print(report.summary())
            path = os.path.join(args.outdir, "longitudinal_identifiability.md")
            with open(path, "w") as fh:
                fh.write(report.to_markdown())
            report.to_json(os.path.join(args.outdir, "longitudinal_identifiability.json"))
            run.log_results({f"contraction.{q['name']}": q["contraction"] for q in report.parameters})
            run.log_result("n_findings", len(report.findings))
        return

    f_data = os.path.join(args.outdir, "longitudinal_data.pkl")
    f_draws = os.path.join(args.outdir, "longitudinal_draws.npz")
    f_sims = os.path.join(args.outdir, "longitudinal_posterior_sims.npz")
    age_mig_NL = load_age_migration()
    rng = np.random.default_rng(args.seed)

    with tracked("paper-longitudinal", params=vars(args), seed=args.seed, enabled=args.track) as run:
        # 1) data
        if args.reuse and os.path.exists(f_data):
            with open(f_data, "rb") as fh:
                d, stan_data = pickle.load(fh)
        else:
            print("Simulating longitudinal data ...")
            d = simulate_data(rng, age_mig_NL, P, legacy_aging=args.legacy_aging)
            stan_data = build_stan_data(d, P["n_mod"])
            with open(f_data, "wb") as fh:
                pickle.dump((d, stan_data), fh)
        print(f"  {stan_data['N']} observations from {stan_data['N_id']} participants")

        # 2) fit
        if args.reuse and os.path.exists(f_draws):
            draws = dict(np.load(f_draws))
        else:
            print("Fitting Stan model ...")
            draws = fit_model(stan_data, args.seed, args.cores, args.outdir,
                              iter_warmup=args.iter // 2, iter_sampling=args.iter // 2)
            np.savez_compressed(f_draws, **draws)
        mu_hat = float(inv_logit(draws["logit_mu"]).mean())
        th_hat = float(np.exp(draws["log_theta"]).mean())
        run.log_results({"mu_posterior_mean": mu_hat, "theta_posterior_mean": th_hat})
        print(f"  posterior mean mu = {mu_hat:.3f} (true {P['mu']}), "
              f"theta = {th_hat:.2f} (true {P['f']})")

        # 3) posterior simulations
        if args.reuse and os.path.exists(f_sims):
            sims = dict(np.load(f_sims))
        else:
            print("Simulating with posterior estimates ...")
            sims = posterior_simulations(draws, args.n_post_sims, args.post_steps,
                                         args.cores, args.seed, sim_params)
            np.savez_compressed(f_sims, **sims)

        # 4) plot
        path = os.path.join(args.outdir, "TimeSeries.pdf")
        plot_figure4(d, draws, sims, age_mig_NL, P, stan_data["Max_age"], path)
        run.add_output(path)
    print(f"Figure written to {path}")
