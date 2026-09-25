# miras

**میراث** — *inheritance, heritage.* The same word in Persian, Turkish and
Azerbaijani (*miras*). Cultural inheritance is what this package models.

**Know whether your study can recover conformity and migration, before you
collect data.**

miras simulates cultural evolution with agent-based models, and then asks the
question that decides whether a study is worth running: *given this design,
can the parameters of the process actually be recovered from the data?* It
simulates the study many times from known parameters, infers them back, and
reports what the design cannot distinguish.

```
pip install miras
```

Python 3.10+. Apache 2.0. One required dependency: numpy.

---

## Built on the Cultural Evolution Workflow

miras exists because of

> Deffner, D., Fedorova, N., Andrews, J. & McElreath, R. (2024). **Bridging
> theory and data: A computational workflow for cultural evolution.**
> *Proceedings of the National Academy of Sciences* 121(48), e2322887121.
> https://doi.org/10.1073/pnas.2322887121 ·
> [code](https://github.com/DominikDeffner/CulturalEvolutionWorkflow)

The paper argues for a workflow: build a generative model of the process,
simulate data from it, and check that your analysis recovers what you put in
*before* collecting real data. Its agent-based model, its three worked
examples, its Stan model and its migration data are all part of miras
(`miras paper ...`). What miras adds is the step the paper does by hand, once
per design, turned into a tool you can run on any design.

**If you use miras, please cite the paper.** The original code is CC0; see
`NOTICE` for the full attribution.

---

## The failure that matters

The paper contains its own motivating example. In its ABC analysis, cultural
F_ST is the only summary statistic. For a population simulated with unbiased
copying (θ = 1) and migration m = 0.3, the published run put 66% of the posterior mass on
θ = 0.5, m = 0.2. Weaker conformity plus less migration produces the same
between-group diversity as the truth.

That is **equifinality**: different processes, indistinguishable data. It is
the problem cultural evolution keeps rediscovering (neutral drift or weak
conformity from frequency data; conformity or migration from F_ST), and it is
invisible from inside a single analysis. The posterior looks like a posterior.
Nothing in the output says the design could never have told the two apart.

---

## The thirty-second version

```python
import miras
from miras import Model, Islands, WrightFisher, Conformity, CrossSectional, ModelSimulator, Uniform

model = Model(structure=Islands(n_groups=20, group_size=50), demography=WrightFisher(),
              learning=Conformity(), innovation=0.05, n_models=20)

study = ModelSimulator(model, summaries=["fst"], n_steps=150,
                       design=CrossSectional(n_per_group=30))      # 30 respondents per village

report = miras.identify(study, {"learning.theta": Uniform(0.5, 3.0),
                                "migration":      Uniform(0.0, 0.4)})
print(report.summary())
```

On a 20-village population with a uniform prior on the conformity exponent
θ ∈ [0.5, 3] and the migration rate m ∈ [0, 0.4] (`examples/equifinality.py`,
2,000 simulated studies, 150 test datasets):

```
=== F_ST only (as in the paper) ===
parameter                contraction  90% coverage  bias (sd)
learning.theta                  0.80          0.89      +0.06
migration                       0.36          0.91      +0.09

[warning] NOT_IDENTIFIED migration (where 1.34 < learning.theta < 2.19)
    The posterior for migration is close to its prior (contraction 0.18 in this
    region): these summaries carry little information about it ...

=== F_ST + within-group diversity ===
learning.theta                  0.83          0.91      +0.03
migration                       0.60          0.91      +0.04

No findings.

=== F_ST + majority share + variants per group ===
learning.theta                  0.83          0.89      +0.03
migration                       0.41          0.90      +0.06

No findings.
Only partly constrained (contraction < 0.5): migration.
```

Three things this says that no single analysis would:

1. **F_ST recovers conformity well but migration badly, and only in part of
   parameter space.** Under moderate conformity, between-group differences are
   maintained by conformity whatever the migration rate, so F_ST says almost
   nothing about migration there. Averaged over the whole prior the problem is
   diluted (contraction 0.36); the regional check finds where it lives.
2. **The fix is a specific measurement, not "more data".** Adding within-group
   diversity, which a survey collects at no extra cost, removes the finding and
   raises migration's contraction from 0.36 to 0.60.
3. **Not every extra summary helps.** Majority share and the number of variants
   per group leave migration only partly constrained (0.41).

**Where the paper's trade-off appears.** I built this example expecting F_ST
alone to produce an `EQUIFINALITY` finding between θ and m, as in the paper's
motivating case. With 20 villages of 50 it does not: the posterior for a
conformist truth runs diagonally (more conformity plus more migration looks
alike), but too diffusely to count as a ridge. With smaller villages it does.
`miras demo` (10 villages of 40, 25 respondents each, 600 simulated studies):

```
=== F_ST only ===
learning.theta                  0.68          0.88      +0.06
migration                       0.48          0.85      +0.17
[warning] EQUIFINALITY learning.theta, migration (where learning.theta > 1.32)
    ... raising learning.theta can be offset by raising migration ...

=== F_ST + within-group diversity ===
learning.theta                  0.76          0.78      +0.11
migration                       0.65          0.75      +0.19
[warning] EQUIFINALITY learning.theta, migration (where learning.theta > 2.03)
```

Within-group diversity shrinks the equifinal region to strong conformity
but does not remove it. The demo is deliberately small, and its 90% intervals
cover the truth only 75–88% of the time; treat its numbers as indicative and
rerun with a larger `--n-reference` before relying on them.

The same question gave a different kind of answer for two population sizes.
That is the point of running the check rather than reasoning about it: which
failure a design has depends on the model, the prior and the design together.
The paper's own case used yet another model (age-structured, with a discrete
four-point prior on θ).

---

## Findings

| Finding | Question it answers |
|---|---|
| `EQUIFINALITY` | Do two parameters trade off against each other, so the data pin down a combination but not each one? Which direction is the trade-off? |
| `NOT_IDENTIFIED` | Is the posterior for this parameter just the prior coming back, with no information even jointly with others? |

Each finding is checked across the whole prior and within regions (thirds of
each parameter's range). A finding confined to a region carries a `where`,
e.g. `where 1.34 < learning.theta < 2.19`: problems that exist only in part of
parameter space are otherwise averaged away.

Alongside the findings, every report gives each parameter's **contraction**
(1 − posterior variance / prior variance: 0 means the data taught nothing,
1 means the parameter is pinned down), the **coverage** of 90% intervals
(should be near 0.90; far below means the inference itself is miscalibrated),
and the **bias**.

### How it decides

For each pseudo-observed dataset the posterior is examined on each prior's
working scale, standardised by the prior SD. A pair of parameters is
*equifinal* in that dataset when their joint posterior is a ridge: much
narrower in one direction than the other, well constrained across the ridge,
with the ridge running diagonally (it mixes both parameters), and with the
pair jointly learned clearly better than either parameter alone. The finding
is raised when that holds in at least 30% of test datasets.

Why not just flag a strong posterior correlation? Because two parameters can
be correlated *and* both well identified; flagging that would make the tool
fire on good designs. The test suite pins this case (`correlated identified`
must stay quiet).

### Why the naive version doesn't work

1. **Marginal posteriors hide equifinality.** Under a product confound each
   parameter's marginal posterior is only moderately narrow, which reads as
   "somewhat identified". The information is in the joint.
2. **Equifinality is not the same as no information.** A parameter in an
   equifinal pair can have low marginal contraction; reporting it as
   `NOT_IDENTIFIED` would send you looking for a missing summary rather than
   a missing *contrast*. miras reports one or the other, never both.
3. **A single test dataset is an anecdote.** Ridges bend: whether θ and m
   trade off can depend on where in parameter space the truth lies. miras
   evaluates many truths, reports how often the ridge appears, and where in
   parameter space.

---

## Comparing designs costs no extra simulations

Build one reference table with every summary you might measure, then evaluate
designs by selecting columns:

```python
table = miras.ReferenceTable.build(study_with_all_summaries, priors, 2000, cores=8)

for summaries in (["fst"], ["fst", "within_diversity"], ["fst", "majority_share", "n_variants"]):
    print(miras.identify(study, priors, table=table.select(summaries)).summary())
```

`examples/equifinality.py` does exactly this; `miras demo` is a smaller,
faster version (a few minutes on one core).

---

## The engine

| Component | Options |
|---|---|
| structure | `Islands(n_groups, group_size, size_grid, r_dist)`: villages on a grid; migrants choose destinations by distance; group sizes conserved |
| demography | `AgeStructured(r_mort, max_age, r_learn, ...)` as in the paper; `WrightFisher()` for non-overlapping generations |
| learning | `Neutral()`, `Conformity(theta)`, `PayoffBias(payoffs, strength)` for frequency-dependent games, `Mixture(rules, weights)` |
| migration | scalar, or age-specific (e.g. the Dutch rates in `miras.paper._data`) |
| variants | infinite alleles (every innovation is new) or a finite set |

```python
res = model.set({"learning.theta": 2.0, "migration": 0.1}).simulate(300, seed=1,
                                                                    record=["fst", "n_variants"])
res.series["fst"]
```

### Checked against things that do not depend on it

| Prediction (`miras.theory`) | Agreement |
|---|---|
| F_ST of the neutral island model, from an identity-by-state recursion | within 1% in three regimes (tested to 6%) |
| Homozygosity of a neutral Wright-Fisher population | within 1% (tested to 5%) |
| Number of variants, Ewens sampling formula | within 6% (diffusion approximation; tested to 10%) |
| Payoff-biased imitation vs. the replicator equation (Hawk-Dove) | max deviation 0.004 over 60 steps |
| Hawk-Dove mixed equilibrium p* = V/C | within 0.02 |
| Coordination game fixates on the side of its unstable point | yes, both sides |
| Conformity exponent orders within-group diversity | θ = 0.8 > 1 > 2 |

`PayoffBias` is the bridge to evolutionary game theory: in a large population
proportional imitation follows the replicator dynamics exactly in
expectation, which is what the test checks.

---

## Inference backends

| Backend | Use |
|---|---|
| `ReferenceTable` | Rejection ABC with local-linear regression adjustment (Beaumont et al. 2002). Amortised: one set of simulations serves every query. Default for `identify`. |
| `ABCSMC` | Sequential Monte Carlo ABC with adaptive tolerances (Beaumont et al. 2009). Sharper posteriors for a single dataset. `identify(..., method="smc")`. |
| Stan | Via CmdStanPy, for likelihood-based models such as the paper's longitudinal model. `analyze()` accepts posteriors from any backend. |

For a model outside miras, wrap any function: `miras.FunctionSimulator(fn)`
with `fn(params: dict, rng) -> summaries`.

---

## The paper's three workflows

```
miras paper dags             # synthetic data from a DAG, power analysis, causal effect
miras paper abm              # migration x conformity sweep, Fig. 3
miras paper longitudinal     # longitudinal Stan model and causal effects, Fig. 4
miras paper longitudinal --identify 9   # new: can the longitudinal design recover mu and theta?
miras paper abc              # the paper's ABC analysis, Fig. 5
```

`--identify` uses Stan as the inference backend: it simulates longitudinal
datasets at known (μ, θ), fits the paper's model to each and hands the
posteriors to `miras.analyze`. Because the role models are observed, even the
tiny `--quick` design recovers both (contraction 0.98–0.99 in the test suite's
two datasets; a smoke test, not a study).

Every workflow has `--quick` for a smoke test, `--cores`, `--seed`,
`--outdir` and `--track`. The full analyses are as heavy as the originals
(tens of CPU-hours for the ABM sweep and the ABC).

These are ports of the original R code, and in porting it a few bugs were
fixed rather than reproduced. Each is marked with a `NOTE` comment:

1. **Power analysis**: the R loop fitted `data[[i]]` (the sweep index) instead
   of `data[[j]]` (the replicate), so all 200 replicates were one dataset.
2. **Longitudinal data**: the first recorded year's group was never filled in,
   so every participant's first analysed year was coded as a migration,
   inflating the estimated migration rates.
3. **Ageing**: in R, `Age[idx[-babies]]` selects nobody when a group has no
   deaths, so nobody in that group ages that year. `AgeStructured(legacy_aging=True)`
   (or `--legacy-aging`) reproduces the original.
4. Smaller: swapped axis labels on the power heat map, a one-year shift of the
   reference curve in Fig. 4c, undefined object names in the ABC plotting code,
   hard-coded plot annotations from one particular run.

The Stan model's array syntax was updated for Stan ≥ 2.33 (the original no
longer compiles); the model is unchanged.

---

## Provenance

An identifiability report is an experiment: it depends on seeds, priors,
summaries and library versions. With [daftar](https://pypi.org/project/daftar/)
installed:

```python
report = miras.identify(study, priors, track=True, label="fst-only-design")
```

records the priors, summaries, miras version and environment, and the
contraction of every parameter, so two reports can be compared with
`daftar diff` rather than eyeballed. The paper workflows take `--track`.
Without daftar this is a no-op with a warning, never an error.

---

## Optional extras

```
pip install "miras[plot]"         # matplotlib: report.plot(), figures
pip install "miras[stan]"         # cmdstanpy (then: python -m cmdstanpy.install_cmdstan)
pip install "miras[provenance]"   # daftar
pip install "miras[paper]"        # everything the paper workflows need
pip install "miras[all]"
```

`miras doctor` shows which of these work in the current environment.

---

## Tests

```
pip install -e ".[dev]"
pytest -q               # engine vs. theory, detectors vs. ground truth
pytest -q --run-slow    # also fits Stan models
```

The detector tests are the ones that matter. Toy simulators with known
identifiability (a product, sum or ratio of two parameters; an irrelevant
parameter; identified, weakly identified and strongly correlated cases) score
each detector in both directions: it must fire where the confound exists and
stay quiet where it does not. See `TESTING.md`.

---

## Status

Research prototype, honestly labelled.

- The thresholds that turn posterior geometry into findings are calibrated on
  toy problems with known answers, not yet on a broad set of real designs.
- Rejection ABC widens posteriors; a parameter can look less identified than
  it is when the reference table is small. Coverage is reported so you can see
  when that happens; more simulations or `method="smc"` sharpen it.
- Equifinality is detected between pairs of parameters; three-way trade-offs
  are on the roadmap.
- Not yet done, and what would decide whether this is useful: applying it to
  published cultural-evolution study designs and checking its verdicts against
  what those studies could and could not conclude.

See `ROADMAP.md`.

## Licence

Apache 2.0. Portions derived from the CC0-licensed Cultural Evolution Workflow
(Deffner et al. 2024); see `NOTICE`.
