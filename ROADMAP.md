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
  `miras commons example`. Same numbers as 0.2.0 for the same seed.
- **0.2.2**: adoption in each group in scenario outputs and reports;
  `--set section.field=value`; `--seed k` in output names; `--no-support`;
  `analyze` keeps same-named files apart and compares runs cell by cell. Same
  numbers as 0.2.1 for the same seed (checked on all four scenario runs).
- **Thirty-four full runs (September–October 2026, 8-core Mac)**: pilot; E1;
  six knockouts; seven backgrounds; two knockouts inside backgrounds; two
  replications; four scenarios; six calibration-sensitivity runs; five runs
  on open questions. Findings: `docs/commons-findings.md` (22 findings);
  tables: `docs/commons-results-*.md`.

### What the planned steps found

Each step was planned in an earlier version of this roadmap; the outcome is
recorded against what was expected.

**September 2026**

1. **Explain the power effect** (`--off power_share`, `--off power_prestige`).
   *Expected:* equal shares remove the effect, prestige does not matter.
   *Found:* exactly that (+0.29 → +0.06; unchanged without prestige).
   **Confirmed: power acts through the allocation of scarce water.**
2. **Explain the tightness effect** (`--off tight_conformity`,
   `--off tight_caution`). *Found:* without conformity the effect disappears
   (−0.44 → −0.06); without caution it stays (−0.41). **Confirmed: conformity,
   not punishment or caution.**
3. **Confirm the ownership mechanism** (`--off ownership_bias`). *Found:* the
   parochialism effect on introduction goes from −0.14 to −0.04.
   **Confirmed.**
4. **One-attribute backgrounds.** *Found:* the neighbours matter more than the
   seed group; tight neighbours block everything; power is relative.

**October 2026**

5. **Cross-checks** (`--background power=high --off power_share`;
   `--background tightness=high --off tight_conformity`). *Expected if the
   mechanisms carry over:* with equal shares a pioneer weaker than its
   neighbours succeeds again; without conformity tight neighbours stop
   blocking. *Found:* both. Single seeds with powerful neighbours 15% → 40%,
   seed power 0 / 0 / 46% → 34 / 41 / 46%; tight background 0% → 88% (every
   group) and 44% / 57% (single seeds). **Confirmed.** New and unexplained:
   with tight neighbours (no conformity) introduction beats origination by
   12 to 14 points at every level of parochialism, and seeding at scarcity
   matters much more (+0.23 to +0.25). See step 2 below.
6. **Replication** (`--seed 2`, `--seed 3`). *Expected:* differences of a few
   points. *Found:* every headline number within 0.01; cell-by-cell
   differences exactly at the size sampling predicts (mean 0.020 against
   0.020 expected). **Confirmed: not Monte Carlo noise.** Also learned: the
   ranking among the ten or so best profiles is noise, and averages over many
   cells are precise enough that 25 runs per cell would do for comparisons
   (step 1 below).
7. **Extreme groups** (`examples/extremes.json`, with two knockouts).
   *Expected from a 10-run test:* 0% everywhere because the two tight groups
   stay out; without conformity, success when Closed is seeded; with equal
   shares, a Marginal seed spreads to Open. *Found at 50 runs:* all three, and
   more precisely: without conformity seeding Closed sustains the commons in
   100% of runs at scarcity (86% introduced during plenty), while seeding
   Dominant or Open reaches every group except Closed and fails (0 to 8%).
   A 6-run check with the parochial filter also off lets Closed adopt from
   any start. Adoption then ends at 0.74 to 0.77 against the 0.75 needed: the
   result sits on a threshold. See step 2.
8. **The example scenario** (Highland, Valley, Riverside): nothing sustained;
   only Valley adopts, Highland (tight, powerful) and Riverside (poor, less
   altruistic) do not.

**October 2026, second round** (steps 1 and 2 of the previous roadmap)

9. **Calibration sensitivity** (`--rho 0.7 --reps 25 --set ...`: β_s 5 and 20,
   θ 1.2 and 2, λ₀ 2 and 8). *Expected:* success rates move; the question was
   whether the signs and order of the effects survive. *Found:* they do in
   all six. Single-seed success ranges from 8% (θ = 2, λ₀ = 2) to 40%
   (θ = 1.2, λ₀ = 8); β_s matters little (19 to 27%). Tightness always hurts,
   a weak pioneer almost never succeeds (12 to 15% only at λ₀ = 8),
   mid-power always beats high power, parochialism matters only on
   introduction, scarcity always beats plenty, and the best starting groups
   are always loose and not weak. **Confirmed: the conclusions do not depend
   on the calibration; the success rates do.** (`docs/commons-results-sensitivity.md`)
10. **(2a) Support** (`--background tightness=high --off tight_conformity
    --no-support`). *Expected if support is the reason:* introduction falls to
    the level of origination (44%). *Found:* exactly 44%, and the two modes
    become indistinguishable cell by cell. **Confirmed.**
11. **(2b) The parochial filter** (`--off tight_conformity,outgroup_filter` on
    the extreme scenario). *Expected:* Closed adopts whatever group the
    practice starts in. *Found:* yes; at scarcity every seeding except
    Marginal's sustains the commons (100%). **Confirmed.**
12. **(2c) The threshold** (`--set resource.rho=0.65`, `0.75`, `--steps 1500`).
    *Expected:* at ρ = 0.75 (A* = 0.625) three adopting groups clear the
    threshold with room to spare. *Found:* **not as expected.** With less
    stress there is less to gain, so adoption stops lower (0.56 to 0.58),
    again just under the threshold with a small shortage left; nothing is
    sustained except with Closed seeded (14%, or 70% introduced during
    plenty). At ρ = 0.65 adoption reaches 0.82 against 0.875. At 1,500 steps
    the outcomes hardly change. Payoff learning alone settles just below the
    threshold at every stress level tried (finding 22).
    (`docs/commons-results-open-questions.md`)

Not yet done: real groups, identifiability.

## Next for miras.commons

Steps 1 and 2 need only what 0.2.2 provides.

### 1. Real groups (E2)

The main remaining step. `miras commons example > groups.json`, then describe
the groups of a real case: sizes and rough positions on each attribute. For a
case such as the Lake Urmia basin, these positions should come from people
who know the communities, or from published survey measures, never from
assigning traits to ethnic or religious groups from outside. The result is
specific to that description: which group to seed, in which mode, and when.

Since the calibration changes success rates (finding 19), run the scenario at
the default and at the two settings that moved them most, and trust only
what the three agree on (each under a minute):

```
miras commons scenario groups.json
miras commons scenario groups.json --set learning.theta=2
miras commons scenario groups.json --set learning.lambda0=8
```

Read the adoption in each group and the shortage, not only the sustained
share (finding 22), and compare the pattern with the extreme case.

### 2. Short follow-ups (optional)

a. **Calibration under mild stress.** The sensitivity runs used ρ = 0.7. The
   two settings that raised success might make mild stress winnable for a
   single seed (0% at the default); about 35 minutes each:

   ```
   miras commons e1 --rho 0.85 --reps 25 --set learning.theta=1.2
   miras commons e1 --rho 0.85 --reps 25 --set learning.lambda0=8
   miras commons analyze commons_output/e1_summary.csv \
       commons_output/e1-rho0.85-set-theta1.2_summary.csv \
       commons_output/e1-rho0.85-set-lambda08_summary.csv --rho 0.85
   ```

b. **The mechanisms at another calibration.** Repeat the two decisive
   knockouts at θ = 2, where success was rarest:

   ```
   miras commons e1 --rho 0.7 --reps 25 --set learning.theta=2 --off power_share
   miras commons e1 --rho 0.7 --reps 25 --set learning.theta=2 --off tight_conformity
   ```

   *Expected:* the power effect shrinks with equal shares and the tightness
   effect without conformity, as at the default.

c. **A longer horizon near the threshold.** Some runs at ρ = 0.75 end just
   under A* with no shortage yet (Closed seeded at scarcity: adoption 0.58,
   shortage 0.00), where the store can only drain very slowly. Whether a
   shortage then appears and adoption recovers needs a much longer run:

   ```
   miras commons scenario examples/extremes.json --off tight_conformity --set resource.rho=0.75 --steps 3000
   ```

### 3. Identifiability (0.2.3)

Which field designs (one survey, repeated surveys, surveys with network
questions, measures of social disapproval) could tell apart the mechanisms
the runs found decisive: "conformity holds the practice back" against
"unequal water shares hold it back", and seed-group effects against
neighbour effects. Uses `miras.identify` with `miras.commons` as the
simulator; needs a small adapter from `CommonsModel` to `ModelSimulator`-style
summaries (adoption per group, share of shortage per group), planned for
**0.2.3**. Also for 0.2.3: an outcome for the small persistent shortage of
finding 22 (e.g. the share of runs whose shortage ends below 2%), since
"sustained" alone counts those runs as failures.

### 4. Variants from the specification

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
