# Testing

```
pip install -e ".[dev]"   # from the source folder; or: pip install "miras[all]" pytest
pytest -q                 # fast suite, under a minute: 91 passed, 1 skipped
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
| 2 | `pytest -q` | 91 passed, 1 skipped (0.1.1) | 76 passed, 1 skipped |
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
