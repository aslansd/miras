# Testing

```
pip install -e ".[dev]"
pytest -q                 # fast suite, about a minute
pytest -q --run-slow      # also fits Stan models (needs CmdStan)
```

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

**Everything else**: engine invariants (group sizes conserved under
migration, models drawn from the learner's own group, exact conformity
probabilities, reproducibility from a seed), inference (ABC recovers an
analytic posterior, prior transforms round-trip), provenance (a daftar run
is recorded; missing daftar is a warning, not an error), and the paper
workflows (Stan input validity, packaged data, priors matching the Stan file).
