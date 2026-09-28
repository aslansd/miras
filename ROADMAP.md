# Roadmap

## Done in 0.1.1

From the first full-scale run on a user's machine (see `TESTING.md`):
convergence of every Stan fit is checked and failures are reported with the
chains responsible; `--identify` leaves unconverged fits out; `--init-radius`
and `--refit`; matplotlib imported lazily; an actionable message when CmdStan
is missing; the ABM sweep and ABC checkpoint and resume exactly; progress lines
estimate the time left; Ctrl-C exits with one line instead of a traceback per
worker; ABC contrasts centred on the posterior. Details in `CHANGELOG.md`.

## Done for miras.commons

- **0.2.0**: the model, experiments E1/E1b/E2/E3, verification checks V1 to
  V9, and the specification amendments A1 to A4 from the pilot.
- **First full runs (September 2026, 8-core Mac)**: pilot; E1 (195,200 runs,
  1 h 45 min); E1b with a low background (2 h 07 min); E3 without sanctions;
  a toy scenario. Findings in the README and `docs/commons-results-0.2.0.md`.
- **0.2.1**: one-attribute backgrounds, condition filters, continuous
  outcomes (`adoption_gap`), `miras commons analyze`, scenario validation and
  `miras commons example`.

## Next for miras.commons

Each step names the question it answers and the commands to run. All
knockouts and backgrounds are run under severe stress only (`--rho 0.7`),
where the seed group matters; mild stress showed no single-seed success in E1.

### 1. Explain the power effect (finding 6)

Power is non-monotonic: a low-power seed group adopts but no one copies it, a
high-power group adopts less itself. Two mechanisms could carry this:
prestige (who gets copied) and the share of water in a shortage (who looks
successful, and who needs the innovation).

```
miras commons e1 --rho 0.7 --off power_share
miras commons e1 --rho 0.7 --off power_prestige
miras commons analyze commons_output/e1_summary.csv \
    commons_output/e1-rho0.7-off-power_share_summary.csv \
    commons_output/e1-rho0.7-off-power_prestige_summary.csv --rho 0.7
```

Expected if the water-share reading is right: without `power_share` the
low-power seed group's innovation spreads and the effect of power shrinks;
without `power_prestige` little changes.

### 2. Explain the tightness effect (finding 3)

Tight seed groups fail with or without sanctions, so conformity or caution
(less experimentation) must carry it.

```
miras commons e1 --rho 0.7 --off tight_conformity
miras commons e1 --rho 0.7 --off tight_caution
```

### 3. Confirm the ownership mechanism (finding 5)

```
miras commons e1 --rho 0.7 --off ownership_bias
```

Expected: the parochialism effect on introduction disappears.

### 4. One-attribute backgrounds (E1b done properly)

Which findings depend on the population around the seed group?

```
miras commons e1 --rho 0.7 --background tightness=low
miras commons e1 --rho 0.7 --background tightness=high
miras commons e1 --rho 0.7 --background wealth=low
miras commons e1 --rho 0.7 --background altruism=low
miras commons e1 --rho 0.7 --background power=high
```

Together steps 1 to 4 are ten runs of about 50 minutes each on 8 cores, so a
long day or two nights. Send the summaries (or the `analyze` report) and the
interpretation goes into a results write-up.

### 5. Real groups (E2)

`miras commons example > groups.json`, edit it to describe the groups of a
case you have in mind (sizes and rough positions on each attribute), and run
`miras commons scenario groups.json`. The answer is specific to that case:
which group to seed, in which mode, and when.

### 6. Calibration sensitivity (amendment A3)

The defaults were chosen so a mid-level population sits near its tipping
point. Rerun the headline comparisons with the payoff-learning slope,
conformity exponent and scarcity value moved up and down, and report which
conclusions survive. Needs a small addition: learning parameters settable from
the command line (for example `--set beta_s=5`), planned for 0.2.2.

### 7. Identifiability

Which field designs (one survey, repeated surveys, surveys with network
questions, measures of sanctions) could tell apart the mechanisms steps 1 to 4
find decisive, using `miras.identify`. This comes last because it depends on
which mechanisms need separating.

### 8. Variants from the specification

Active rejection of owned traits (D4c, already a switch:
`ownership_rejection`), targeted first adopters (D3b), and imposition of the
innovation by powerful groups (D8).

## Next for the paper workflows (was 0.1.2)

1. **Evidence on stuck chains.** Refit the full-scale longitudinal data with
   several seeds, with and without `--init-radius 0.5`, and record how often a
   chain gets stuck. Change the default initialisation only if the evidence
   supports it. Also check whether the original R/rstan fit shows the same
   behaviour, to tell a property of the model from a property of the port.
2. **Resumable `--identify`.** Each dataset takes about two hours; save each
   finished fit so an interrupted run skips completed datasets, and run
   datasets in parallel when there are cores to spare (each fit already uses
   four).
3. **Checkpoint the remaining long steps**: ABC posterior predictions and the
   longitudinal posterior simulations (minutes rather than hours, so lower
   priority).

## Later

Ordered by what most improves the one question miras exists to answer:
*can this study design recover these parameters?*

1. **More findings.** `UNDERPOWERED` (how many groups / respondents / waves
   until a parameter is recoverable: the paper's power analysis, generalised
   by sweeping the design) and `MISCALIBRATED` (simulation-based calibration,
   Talts et al. 2018, rather than the single 90% coverage number reported now).
2. **Equifinality beyond pairs.** The current detector examines parameter
   pairs. Ridges involving three or more parameters (e.g. conformity, migration
   and innovation jointly) need the full posterior covariance spectrum.
3. **Summary informativeness.** A `WEAK_SUMMARY` finding saying which
   summaries carry information about which parameters, so designs can be
   pruned as well as extended.
4. **Simulation-based inference backend** (neural posterior estimation via
   `sbi`), for designs where ABC's curse of dimensionality bites.
5. **Longitudinal designs as first-class objects**, not only through the paper
   workflow: panel studies with observed networks, as in Fig. 4.
6. **More learning rules and structures.** Prestige / success bias, guided
   variation and content bias; network population structure.
7. **Speed.** A JAX backend (`vmap` over parameter sets) so reference tables
   of 10^5 simulations become interactive.
8. **Real data adapters**, and a validation study: does a design that miras
   calls identifiable actually recover parameters from real data?
9. Populations of LLM agents as learners, audited with daftar's Concordia
   adapter.
