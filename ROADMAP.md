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
- **Forty-two full runs (September–October 2026, 8-core Mac)**: pilot; E1;
  six knockouts; seven backgrounds; two knockouts inside backgrounds; two
  replications; four scenarios; six calibration-sensitivity runs; five runs
  on open questions; eight follow-ups. Findings: `docs/commons-findings.md`
  (28 findings);
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

**October 2026, third round** (the optional follow-ups 2a to 2c)

13. **(2a) Calibration under mild stress** (`--rho 0.85 --reps 25`, θ = 1.2
    and λ₀ = 8). *Expected:* the two settings that raised success under
    severe stress might make mild stress winnable for a single seed.
    *Found:* only λ₀ = 8 does (single seeds 34 to 40%, every group 89%);
    θ = 1.2 leaves single seeds at 0% (every group 34% → 55%). With λ₀ = 8
    the severe-stress patterns reappear. **Partly confirmed: under mild
    stress the barrier is the value of saving, not conformity** (finding 23).
14. **(2b) Knockouts at θ = 2.** *Expected:* the power effect shrinks with
    equal shares and the tightness effect without conformity, as at the
    default. *Found:* the tightness part holds (without conformity θ no
    longer matters at all, finding 24), but **equal shares barely help at
    θ = 2** (8–9% → 12–13%) and the power effect does not shrink: when
    conformity stops almost every start, the water-share barrier has little
    left to block (finding 25).
15. **(2c) 3,000 steps near the threshold** (ρ = 0.75). *Expected:* tell a
    slow drain from a steady state. *Found:* seedings with a lasting shortage
    do not change; the two cells near A* move toward the same state from
    opposite sides (Closed seeded at scarcity 14% → 64%; introduced during
    plenty 70% → 30%). **500 steps is not long enough near the threshold**
    (finding 26). (`docs/commons-results-followups.md`)

**October 2026, fourth round** (the two optional runs)

16. **(2a) Does the horizon change E1?** (`--rho 0.7 --reps 25 --steps 2000`).
    *Expected:* the main effects keep their signs; cells near the threshold
    move. *Found:* both. Every sign holds and the references barely change
    (single seeds 26 / 31% against 25 / 25%), but the tightness effect
    shrinks (−0.44 → −0.26): tight seeds gain (1% → 9 to 12%) because their
    neighbours pick the practice up given time, loose seeds lose (46% →
    37%) because more of their runs end just under the threshold. The best
    starting groups become middling rather than loose. **Confirmed, with a
    qualification of finding 3** (finding 27).
17. **(2b) The mechanisms under mild stress** (`--rho 0.85 --reps 25 --set
    learning.lambda0=8`, `--off power_share` and `--off tight_conformity`).
    *Found:* equal shares remove the power effect completely (+0.34 → 0.00);
    without conformity the tightness effect almost disappears (−0.50 →
    −0.17). **Confirmed: the same mechanisms as under severe stress**
    (finding 28). (`docs/commons-results-followups.md`, parts d and e)

Not yet done: real groups (no data yet), identifiability.

## Next for miras.commons

### 1. Identifiability (0.2.3)

Which field designs (one survey, repeated surveys, surveys with network
questions, measures of social disapproval) could tell apart the mechanisms
the runs found decisive: "conformity holds the practice back" against
"unequal water shares hold it back" (findings 4, 6 and 25 show that which
one binds depends on the calibration, so a design that can tell them apart
matters), and seed-group effects against neighbour effects. Uses
`miras.identify` with `miras.commons` as the simulator; needs a small adapter
from `CommonsModel` to `ModelSimulator`-style summaries (adoption per group,
share of shortage per group), planned for **0.2.3**. Also for 0.2.3, from
findings 22 and 26:

- an outcome for the small persistent shortage (e.g. the share of runs whose
  shortage ends below 2%), since "sustained" alone counts those runs as
  failures;
- a convergence check: compare the last two 100-step windows and flag cells
  whose adoption is still moving, so a provisional result is marked as such.

### 2. No further runs needed with 0.2.2

Every question the runs raised has been answered with what 0.2.2 provides.
The next useful runs need the convergence check of step 1: findings 26 and
27 show that 500 steps is not always enough, so 0.2.3 should flag unsettled
cells, and a longer default horizon (2,000 steps) should be considered once
its cost is known (a 25-run severe-stress E1 at 2,000 steps is about four
times as long as at 500).

### 3. Real groups (E2), when data become available

`miras commons example > groups.json`, then describe the groups of a real
case: sizes and rough positions on each attribute. For a case such as the
Lake Urmia basin, these positions should come from people who know the
communities, or from published survey measures, never from assigning traits
to ethnic or religious groups from outside. The result is specific to that
description: which group to seed, in which mode, and when. Run it at the
default and at the two settings that moved results most, use a longer
horizon (finding 26), and trust only what the three agree on:

```
miras commons scenario groups.json --steps 2000
miras commons scenario groups.json --steps 2000 --set learning.theta=2
miras commons scenario groups.json --steps 2000 --set learning.lambda0=8
```

Read the adoption in each group and the shortage, not only the sustained
share (finding 22).

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
