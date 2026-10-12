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
- **0.2.1**: one-attribute backgrounds, condition filters, continuous
  outcomes (`adoption_gap`), `miras commons analyze`, scenario validation and
  `miras commons example`. Gives the same numbers as 0.2.0 for the same seed.
- **Fourteen full runs (September–October 2026, 8-core Mac)**: pilot; E1;
  E3 without sanctions (all conditions); E1b with all five background
  attributes low and with tightness low (all conditions); and, under severe
  stress (`--rho 0.7`), five knockouts and five one-attribute backgrounds; plus
  the example scenario. Results: README ("What the runs show"),
  `docs/commons-results-0.2.0.md`, `docs/commons-results-knockouts.md`,
  `docs/commons-results-backgrounds.md`.

### What the planned steps found

Each step below was planned in the previous version of this roadmap; the
outcome is recorded against what was expected.

1. **Explain the power effect.** Ran `--off power_share` and
   `--off power_prestige`. *Expected:* if the water-share reading is right,
   equal shares remove the effect and prestige does not matter. *Found:*
   exactly that. Power effect on the sustained share +0.29 → +0.06 with equal
   shares, unchanged without prestige; a weak seed group goes from 0% to 41%.
   **Confirmed: power acts through the allocation of scarce water.**
2. **Explain the tightness effect.** Ran `--off tight_conformity` and
   `--off tight_caution` (sanctions had been ruled out by the earlier E3).
   *Found:* without conformity the effect disappears (−0.44 → −0.06); without
   caution it stays (−0.41). **Confirmed: conformity, not punishment or
   caution, makes tight groups poor starting points.**
3. **Confirm the ownership mechanism.** Ran `--off ownership_bias`.
   *Expected:* the parochialism effect on introduction disappears. *Found:*
   −0.14 → −0.04, and introduction succeeds about twice as often (49% vs 25%).
   **Confirmed.**
4. **One-attribute backgrounds.** Ran tightness low and high, wealth low,
   altruism low and power high. *Found:* the surrounding groups matter more
   than the seed group. Tight neighbours block everything (0%, even with every
   group seeded); loose neighbours raise single-seed success to 41% and make
   mild stress winnable; poorer or less altruistic neighbours almost block
   single seeds (4%, 0%); with more powerful neighbours only an equally powerful
   seed group succeeds, so **power is relative**. The direction of the
   tightness and altruism effects held in every background where anything
   succeeded.

Not yet done from the earlier plan: E2 with real groups (only the example
scenario was run), calibration sensitivity, identifiability.

## Next for miras.commons

All of steps 1 to 3 need no new code.

### 1. Cross-checks: are the background effects carried by the same mechanisms?

Finding 7 (neighbours) is the newest and least explained result. Two
knockouts inside the backgrounds that changed the answer would test whether
the mechanisms found for the seed group also operate through the neighbours:

```
miras commons e1 --rho 0.7 --background power=high --off power_share
miras commons e1 --rho 0.7 --background tightness=high --off tight_conformity
miras commons analyze commons_output/e1b-power-high-rho0.7_summary.csv \
    commons_output/e1b-power-high-rho0.7-off-power_share_summary.csv --rho 0.7
```

*Expected if the mechanisms carry over:* with equal shares, a seed group
weaker than its neighbours succeeds again; without conformity, tight
neighbours stop blocking the practice.

### 2. Replication with another seed

Every result so far comes from one master seed. Rerunning the severe-stress
E1 with `--seed 2` (`miras commons e1 --rho 0.7 --seed 2`, about 50 minutes)
and comparing it with `analyze` checks that the effects are larger than
Monte Carlo noise. Differences of a few percentage points are expected;
changes of direction would be a red flag.

### 3. Real groups (E2)

`miras commons example > groups.json`, then describe the groups of a real
case: sizes and rough positions on each attribute. For a case such as the
Lake Urmia basin, these positions should come from people who know the
communities, or from published survey measures, never from assigning traits
to ethnic or religious groups from outside. The result is specific to that
description: which group to seed, in which mode, and when.

### 4. Calibration sensitivity (amendment A3), with 0.2.2

The defaults were chosen so a mid-level population sits near its tipping
point. Rerun the headline comparisons (tightness, power, ownership,
neighbours) with the payoff-learning slope, conformity exponent and scarcity
value moved up and down, and report which conclusions survive. Needs one
addition, planned for **0.2.2**: model parameters settable from the command
line, e.g. `--set learning.beta_s=5 --set learning.theta=2`, included in the
output file names and checkpoint keys.

### 5. Identifiability

Which field designs (one survey, repeated surveys, surveys with network
questions, measures of social disapproval) could tell apart the mechanisms
the runs found decisive: "conformity holds the practice back" against
"unequal water shares hold it back", and seed-group effects against
neighbour effects. Uses `miras.identify` with `miras.commons` as the
simulator; needs a small adapter from `CommonsModel` to `ModelSimulator`-style
summaries (adoption per group, share of shortage per group), also planned for
0.2.2.

### 6. Variants from the specification

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
