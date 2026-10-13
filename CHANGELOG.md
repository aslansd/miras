# Changelog

## Unreleased

Documentation only (no code changes), from the second round of October runs
(calibration sensitivity with `--set`, `--no-support`, and three scenario
checks).

- `docs/commons-findings.md`: findings 19 to 22 (the conclusions survive the
  calibration; outside support explains why introduction can beat
  origination; the parochial filter keeps the closed group out; payoff
  learning alone settles just below the threshold, at every stress level
  tried), and corrections to findings 12, 17 and 18.
- New raw reports: `docs/commons-results-sensitivity.md` and
  `docs/commons-results-open-questions.md`.
- README, ROADMAP (what each step found against what was expected; next:
  real groups at three calibrations, short follow-ups, identifiability in
  0.2.3) and TESTING (checks C14 to C16).


## 0.2.2 — 2026-10-13

From the October runs of `miras.commons` (cross-checks, replications with
seeds 2 and 3, and the extreme-group scenarios). Gives the same numbers as
0.2.1 for the same seed and settings; this was checked on all four scenario
runs.

**Experiments**
- Scenario outputs give the adoption in each group (mean of the last 100
  steps): `adoption_<group>` columns in the runs and summary CSVs, and a
  per-group table in the report. This is what explained every scenario
  result so far, and it replaces the helper script `examples/per_group.py`.
- `--set section.field=value` (repeatable) on `miras commons e1` and
  `scenario` changes any field of `learning`, `innovation` or `resource`,
  for calibration sensitivity (amendment A3) without editing code. Values
  are type-checked, unknown names are reported with the list of valid ones,
  and `resource.rho` in E1 points to `--rho`.
- `--no-support`: an introduced innovation comes without the subsidy and the
  outside demonstrators.
- Output names now say everything that differs from the defaults:
  `-off-...`, `-nosupport`, `-set-...`, `-steps<n>` and `-seed<k>`. In 0.2.1
  a second seed or a different number of steps overwrote the first run's
  files unless a separate `--outdir` was used. Runs with the default seed and
  steps keep their 0.2.1 names.

**Analysis**
- `analyze` keeps summaries with the same file name apart (prefixing the
  folder) instead of silently keeping only the last one.
- With several summaries, a cell-by-cell comparison: correlation, mean
  absolute difference of the sustained share and the difference sampling
  alone would produce. For replications it says whether two runs differ by
  more than Monte Carlo noise; for knockouts, how much a mechanism changes
  individual cells.

**Documentation**
- `docs/commons-findings.md`: eighteen findings from twenty-three full runs,
  with the numbers. New raw reports: `commons-results-e1.md` (the E1 report the
  README referred to as `commons-results-0.2.0.md`, which was missing),
  `-crosschecks.md`, `-replication.md`, `-scenarios.md`; the knockout and
  background reports regenerated in the same format, each with the command
  that reproduces it.
- The model specification moved to `docs/commons-specification.pdf`;
  `docs/commons-model.md` documents `--set`.
- README, ROADMAP, TESTING and PUBLISHING updated; the ROADMAP records what
  each planned step found against what was expected, and the next steps
  (calibration sensitivity with `--set`, three open questions, real groups,
  identifiability).
- Unreleased documentation changes after 0.2.1 (findings 1 to 10, the
  knockout and background reports, TESTING checks C8 to C10) are part of
  this release.

**Repository**
- Removed files that are generated or duplicated: `dist/` and
  `src/miras.egg-info/` (built fresh for each release), `groups.json`
  (identical to `miras commons example`), `examples/per_group.py` (now in the
  scenario report), and the `replication2.md` / `replication3.md` outputs
  (now `docs/commons-results-replication.md`). The seed-2 and seed-3 outputs
  moved from `commons_output_seed2/` and `commons_output_seed3/` to
  `commons_output/` under their 0.2.2 names. `.gitignore` now covers build
  output, tool caches and checkpoints.


## 0.2.1 — 2026-09-28

From the first full runs of `miras.commons` on a user's machine (pilot, E1,
E1b with a low background, E3 without sanctions, and a scenario).

**Experiments**
- One attribute at a time for the background groups (E1b):
  `--background tightness=low` or `--background tightness=low,power=high`;
  `low`, `mid` and `high` still set all five. The 0.2.0 E1b changed all five
  attributes at once, so it could not say which one mattered.
- Condition filters for `miras commons e1`: `--rho`, `--contact`, `--timing`.
  A knockout under severe stress only (`--rho 0.7 --off power_share`) takes
  half the time of a full E1. Output files are named after the filters.
- Two continuous outcomes in every run: `a_star` (the adoption share the
  commons needs) and `adoption_gap` (mean adoption over the last 100 steps
  minus `a_star`). The binary `sustained` hid that the low-background E1b
  spread the innovation widely but stalled just short of the threshold.

**Analysis**
- `miras commons analyze SUMMARY.csv [MORE ...]`: overview of sustained
  shares and adoption gaps; main effects of each seed attribute; where
  adoption happens by the seed group's power; tightness by power; introduce
  minus originate by parochialism; scarcity minus plenty; the best seed groups;
  and, for several files, effect sizes side by side on the sustained share and
  on mean adoption (backgrounds for E1b, knockouts for E3). Reads 0.2.0
  summaries too. Numpy only. `--out` writes the report to a file.
- `docs/commons-results-0.2.0.md`: that analysis applied to the 0.2.0 runs.

**Scenarios**
- A missing or malformed scenario file now gives one line saying what to
  change (missing file, invalid JSON, empty or duplicate groups, unknown
  fields in any section, unknown timings) instead of a traceback; exit status 2.
- `miras commons example > groups.json` prints an example scenario with three
  groups; the same file ships as `examples/commons_scenario.json`.

**Tests**: 20 new (`tests/test_commons_v021.py`); 130 passed, 1 skipped.


## 0.2.0 — 2026-09-27

**New: `miras.commons`**, a model of culturally different groups sharing a
common-pool resource, and of how to seed a resource-saving innovation so that
it spreads (the miras.commons model specification, with amendments A1 to A4).
- Groups differ in tightness (conformity, sanctions, caution), in-group
  altruism, out-group parochialism, wealth, political power and contact; the
  innovation originates in a group or is introduced from outside (ownership
  tags, subsidy, outside demonstrators), during plenty or at scarcity.
- Resource with recharge and storage, water-filling allocation under shortage
  (power-weighted between groups, equal quotas within), efficiency or
  sufficiency innovations.
- Experiments E1 (seed-group factorial), E1b (background levels), E2 (your own
  scenarios from JSON) and E3 (mechanism knockouts): `miras commons
  {pilot,e1,scenario}`, with CSV and Markdown outputs, exact checkpoint/resume
  and daftar tracking.
- Verification checks V1 to V9 against known results (`tests/test_commons.py`).

**Engine**
- `miras.engine.groups.GroupedPopulation`: groups of unequal size, and model
  choice across groups by contact, prestige and a parochial filter;
  `water_fill` for proportional allocation with caps. The equal-sized
  `Population` behind the paper models is unchanged.
- The long-run helpers moved to `miras.runner` (the old `miras.paper._runner`
  still works).


## 0.1.1 — 2026-09-26

Fixes from the first full-scale end-to-end check of 0.1.0 (macOS, 8 cores).

**Convergence**
- Every Stan fit (`miras paper dags`, `miras paper longitudinal`) is checked:
  converged means all R-hat ≤ 1.01 and no divergent transitions. Otherwise
  miras prints a per-chain table naming suspect chains (mostly divergent, or
  far from the other chains), marks the Fig. 4 PDF "Stan fit did NOT
  converge", and saves `convergence-seed-<seed>.json`. Caches loaded with
  `--reuse` are checked too. New: `miras.inference.stan.assess_chains`,
  `convergence`, `Convergence`.
- `--identify` leaves unconverged fits out of the report and lists them in its
  notes; `--keep-unconverged` keeps them. Reports show `info["notes"]`.
- `--init-radius R` (start chains in (−R, R) on the unconstrained scale) and
  `--refit` (reuse cached data, redo fit and posterior simulations).
- Each fit writes to its own `stan_output/seed-<seed>/` folder, so refits no
  longer mix CSV files from different fits (which made `cmdstanpy.from_csv`
  fail).

**Long runs**
- `miras paper abm` and `miras paper abc` checkpoint every two minutes and on
  Ctrl-C, and resume with results identical to an uninterrupted run
  (`--fresh` starts over).
- Progress lines estimate the time left.
- Ctrl-C prints one line and exits with status 130; worker processes no longer
  print tracebacks.

**ABC**
- Contrasts (panels c, f) are centred on the posterior's most common migration
  value instead of cells hard-coded from the paper's run; each panel states
  its centre. `--paper-contrasts` restores the original. Labels no longer
  cover the densities.

**Packaging and messages**
- matplotlib is imported lazily in `miras.paper`, so the core install can
  build Stan data and run the test suite (tests needing extras skip).
- When CmdStan is missing, the error says to run `install_cmdstan` and how to
  fix `SSL: CERTIFICATE_VERIFY_FAILED` on macOS.

**Documentation**
- README: installing CmdStan, measured run times, what the full-scale runs
  show, expected output of the thirty-second example, convergence of the
  longitudinal fit. TESTING: an end-to-end release checklist. PUBLISHING: the
  procedure as used, and why a PyPI page changes only with a new version.

## 0.1.0 — 2026-09-24

First release.

- **Engine.** Agent-based model of cultural transmission with pluggable
  structure (`Islands`), demography (`AgeStructured`, `WrightFisher`) and
  learning rules (`Neutral`, `Conformity`, `PayoffBias`, `Mixture`);
  infinite-alleles or finite variant sets; scalar or age-specific migration.
  Any nested parameter can be set by name (`model.set({"learning.theta": 2})`).
- **Theory.** `miras.theory` gives analytic predictions (island-model
  identity and F_ST, neutral homozygosity, Ewens variant counts, replicator
  dynamics) that the engine is tested against.
- **Inference.** Priors with working and unbounded scales; ABC with a reusable
  reference table and local-linear regression adjustment; ABC-SMC; Stan
  backend via CmdStanPy.
- **Identifiability report.** `identify()` and `analyze()` with two findings,
  `EQUIFINALITY` and `NOT_IDENTIFIED`, pinned by sensitivity and
  specificity tests on toy simulators with known answers.
- **The paper.** The three workflows of Deffner et al. (2024) as
  `miras paper {dags,abm,longitudinal,abc}`, plus a Stan identifiability
  mode for the longitudinal design (`--identify N`).
- **Provenance.** `track=True` / `--track` records runs with daftar; a no-op
  when daftar is not installed.
- **CLI.** `miras demo`, `miras doctor`, `miras paper`.
