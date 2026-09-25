# Changelog

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
