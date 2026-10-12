# Testing

```
pip install -e ".[dev]"   # from the source folder; or: pip install "miras[all]" pytest
pytest -q                 # fast suite, under a minute: 130 passed, 1 skipped
pytest -q --run-slow      # also fits Stan models (needs CmdStan, ~10 min)
```

With only the core install (numpy), the suite still runs: tests that need
matplotlib, pandas, daftar or CmdStan skip themselves. (In 0.1.0 two tests
failed instead, because `miras.paper` imported matplotlib at module level;
fixed in 0.1.1 and pinned by `test_paper_modules_import_without_matplotlib`.)

The tests fall into three groups, and the first two are the ones that matter.

**The engine against theory** (`tests/test_theory.py`). Every prediction
comes from `miras.theory`, which is derived independently of the simulation
code: the neutral island model's F_ST (from an identity-by-state recursion),
neutral homozygosity, Ewens variant counts, and the replicator dynamics that
payoff-biased imitation follows in a large population (including the
Hawk-Dove mixed equilibrium and fixation in a coordination game). Agreement
here is evidence that the engine implements the model it claims to.

**The detectors against ground truth** (`tests/test_identify.py`). Toy
simulators (`tests/toys.py`) whose identifiability is known by construction:
a product, a sum or a ratio of two parameters (equifinal), an irrelevant
parameter (not identified), and several identified cases including a weakly
identified one and a strongly correlated one. Both directions are tested:

- **sensitivity**: each equifinal or uninformative toy must raise its finding;
- **specificity**: identified toys must stay quiet, because a detector that
  fires on everything is worse than no detector.

The thresholds in `miras.identify.Thresholds` are pinned by these tests.
Change one and the suite tells you which boundary moved.

**The convergence check against known failures** (`tests/test_v011.py`).
The same both-directions logic as the detectors, for Stan fits: a synthetic
copy of the stuck chain from the 0.1.0 end-to-end check (one chain diverging
on all 1,500 iterations at log θ = −1.2) must be named as the suspect chain; a
chain far from the others without divergences must be named too; a fit that
struggles everywhere must be reported without blaming one chain; a single
divergence must fail the fit; and a healthy fit must pass.

**Resuming is exact** (`test_abm_sweep_resumes_to_identical_results`). A
sweep resumed from a half-finished checkpoint must equal the uninterrupted
sweep bit for bit. The same was checked by hand with a real Ctrl-C (SIGINT)
halfway through a 462-simulation sweep.

**`miras.commons` against known results** (`tests/test_commons.py`). The
nine verification checks of the model specification (V1 to V9): resource
bookkeeping and the exact step of the first shortage, the sustainability
threshold ρ ≥ 1 − δ, water-filling allocation, the replicator decline under
plenty, the shortage-equals-cost equilibrium under rationing, conformity
fixation, symmetry between identical groups, containment by full
parochialism, and exact reproduction and resumption. Also: the no-innovation
reference has no adopters, and ownership bias slows introduction into a
parochial seed group.

**`miras.commons` tools from 0.2.1** (`tests/test_commons_v021.py`):
one-attribute backgrounds change only the named attribute and reject unknown
names or levels; condition filters give exactly the expected cells; summaries
written by 0.2.0 still build and analyse; `adoption_gap` equals mean adoption
minus A*; every kind of scenario-file mistake (missing file, invalid JSON, empty
or duplicate groups, unknown fields in any section, unknown timings) gives a
one-line message and exit status 2, never a traceback; the example scenario is
valid; and `miras commons analyze` produces every section, for one file and
for a comparison of several. The analysis was also checked by hand against
the 0.2.0 runs: its tables reproduce the numbers computed directly from the
summaries.

**Everything else**: engine invariants (group sizes conserved under
migration, models drawn from the learner's own group, exact conformity
probabilities, reproducibility from a seed), inference (ABC recovers an
analytic posterior, prior transforms round-trip), provenance (a daftar run
is recorded; missing daftar is a warning, not an error), and the paper
workflows (Stan input validity, packaged data, priors matching the Stan file).

## End-to-end checks before a release

The unit tests cannot cover the full-scale workflows, which take hours.
Before a release, run these on a real machine and compare with the expected
results. The reference values below come from the 0.1.0 check on an 8-core
Apple Silicon Mac (Python 3.11, CmdStan 2.40).

| # | Command | Expected | 0.1.0 result |
|---|---|---|---|
| 1 | `miras doctor` | every line `ok` | ok |
| 2 | `pytest -q` | 130 passed, 1 skipped (0.2.1) | 76 passed, 1 skipped |
| 3 | the README's thirty-second example | `NOT_IDENTIFIED migration` in a region around 1.4 < θ < 2.2; θ contraction about 0.8 | contraction 0.82 / 0.39, region 1.46–2.2 |
| 4 | `miras paper dags` | causal effect near 2 (seed 1: 1.87) | 1.87, identical to Linux |
| 5 | `miras paper abm` | Fig. 3 pattern: conformity keeps F_ST high, migration lowers it, largest causal effect at θ = 1.4 | ok, 7.4 h |
| 6 | `miras paper longitudinal` | converged (R-hat ≤ 1.01, 0 divergences), μ ≈ 0.1, θ ≈ 3; from 0.1.1 a failed fit prints a `NOT CONVERGED` table naming the chain | **failed**: R-hat 1.62, 1,500 divergences (one stuck chain); 0.1.0 did not warn |
| 7 | `miras paper longitudinal --identify 9` | a report; every fit converged | not completed (stopped during fit 2; fit 1 R-hat 1.16) |
| 8 | `miras paper abc` | unbiased case: most mass on θ = 1, m = 0.3; contrast panels say `around m = ...` (0.1.1) | 94% on truth; conformist case lands on θ = 3, m = 0.2 (see README) |
| 9 | interrupt `miras paper abm` with Ctrl-C, then rerun the same command | `Interrupted after k/46200`, exit status 130, then `resuming: k/46200 simulations already done` | new in 0.1.1 |

Notes for reading the output:

- Stan prints `normal_lpdf: Scale parameter is 0` and similar messages early in
  warm-up. These are harmless on their own; the convergence line printed after
  each fit is what counts.
- For check 6, a divergence count equal to a multiple of the post-warm-up draws
  per chain (1,500 by default) points to whole chains being stuck; 0.1.1 names
  them. Refit with `--refit --seed 2` (and optionally `--init-radius 0.5`), and
  record in this table whether the refit converged: that is the evidence the
  roadmap needs before changing the default initialisation.
- The ABC workflow warns when fewer than 100 posterior rows exist for a
  contrast and resamples. In 0.1.0 this happened for the unbiased contrasts
  (12 rows at the hard-coded m = 0.2); from 0.1.1 contrasts start from the
  posterior's most common migration value, which usually has many rows.
- In 0.1.0, interrupting a long run with Ctrl-C printed a `KeyboardInterrupt`
  traceback from every worker. From 0.1.1 it prints one line saying where
  progress was saved.

## End-to-end checks for `miras.commons`

Run on an 8-core Apple Silicon Mac with miras 0.2.0 (C1 to C5) and 0.2.1
(C6, C8 to C10), September and October 2026; both versions give identical
numbers for the same seed. The expected values are what those runs gave; the "sustained" shares are averages
over 50 runs per cell, so expect differences of a few percentage points on
another machine or seed, not changes of direction.

| # | Command | Time | Expected | 0.2.0 result |
|---|---|---|---|---|
| C1 | `miras commons pilot` | 2 min | no innovation: 0% sustained, shortage exactly 0.150 (ρ 0.85) and 0.300 (ρ 0.7); every group seeded at scarcity under ρ 0.7: 100% | as expected; closely matches the development pilot |
| C2 | `miras commons e1 --cores 8` | 1 h 45 min | ρ 0.85: 0% sustained from any single seed; ρ 0.7: about 25%, best profiles about 95%; tightness effect about −0.44 | as expected (see `docs/commons-results-0.2.0.md`) |
| C3 | `miras commons e1 --background low` | 2 h 07 min | 0% sustained, but a smaller adoption gap than C2 | 0% sustained; adoption gap −0.27 vs −0.43 |
| C4 | `miras commons e1 --off tight_sanctions` | about 1 h 45 min | every-group seeding under ρ 0.7 falls from about 96% to about 9%; tightness effect survives (about −0.40) | as expected |
| C5 | `miras commons scenario groups.json` | under a minute | a report ranking seed groups | 0.2.0 failed with a traceback when the file was missing; 0.2.1 prints one line saying how to create it (`miras commons example > groups.json`) |
| C6 | `miras commons analyze commons_output/e1_summary.csv commons_output/e1b-low_summary.csv commons_output/e1-off-tight_sanctions_summary.csv` | seconds | the tables in `docs/commons-results-0.2.0.md` | new in 0.2.1 |
| C7 | interrupt any `miras commons e1` with Ctrl-C, then rerun it | | `resuming: k/N runs already done`, identical results | checked in development (`test_v9_resumed_experiment_is_identical`) |
| C8 | the five severe-stress knockouts (`--rho 0.7 --off ...`), compared with `analyze` | about 50 min each | effect on sustained share (high − low), originate: tightness −0.06 without `tight_conformity`, −0.41 without `tight_caution`; power +0.06 without `power_share`, +0.28 without `power_prestige`; parochialism on introduction −0.04 without `ownership_bias` | as expected (0.2.1; `docs/commons-results-knockouts.md`) |
| C9 | the one-attribute backgrounds (`--rho 0.7 --background ...`) | about 50 min each | single-seed sustained share: tightness=low 41%, tightness=high 0% (every group seeded also 0%), wealth=low 4%, altruism=low 0%, power=high 15% | as expected (0.2.1; `docs/commons-results-backgrounds.md`) |
| C10 | `miras commons e1 --background tightness=low` (all conditions) | about 1 h 45 min | under mild stress single seeds sometimes succeed (12 to 17%), unlike the mid background (0%) | as expected (0.2.1) |

Notes for reading the output:

- The binary `sustained` outcome can be 0% while a lot is happening; read it
  together with `adoption_gap` (0.2.1) and the adoption columns.
- A knockout run is compared with the matching E1 run by `analyze`; with
  `--rho 0.7`, compare against E1 restricted the same way (`analyze ... --rho 0.7`).
