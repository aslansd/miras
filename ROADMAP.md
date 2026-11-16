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
- **0.2.3**: `miras commons identify` (field designs for identifiability);
  each group's water shortfall; the outcomes `low_shortage`, `adoption_drift`
  and `settled`. Same numbers as 0.2.2 for every outcome 0.2.2 had.
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

**November 2026** (step 1 of the previous roadmap)

18. **Identifiability** (`miras commons identify` on the example scenario,
    introduced into Valley, into Highland, and seeded everywhere, 12,000
    simulations each). *Asked:* which field designs could tell "conformity
    holds the practice back" from "unequal water shares hold it back".
    *Found:* water-delivery records recover the power weighting of shares
    almost completely (contraction 0.87 to 0.99; one survey 0.46 to 0.59).
    Conformity is the hard one: one survey 0.23 to 0.38, five waves plus
    records 0.49 to 0.62, and not identified at all from a survey with
    records wherever shares are strongly unequal. No design confuses the two
    (no equifinality). A first try with 3,000 simulations gave unstable
    results for the 30-number designs, so the default is now 12,000.
    (`docs/commons-identifiability.md`, findings 29 to 31)
19. **The two outcomes** asked for by findings 22 and 26 (`low_shortage`,
    `settled`) are in every run from 0.2.3, and `analyze` reports how runs
    end.

**November 2026, second round** (the optional runs with 0.2.3)

20. **(2a) More respondents or more waves** (`--seed-group Valley
    --respondents 400`; `--waves 10`). *Asked:* is the limit on conformity
    sampling or the model's randomness? *Found:* the model's randomness. Four
    times as many respondents adds 0.01 to 0.03 to the contraction of θ;
    twice as many waves adds 0.07 to 0.11 (best design 0.51 → 0.58). Larger
    surveys shrink the region where unequal shares hide conformity (γ > 0.70
    → γ > 1.33) but do not remove it (finding 32).
21. **(2b) The extreme groups** (`examples/extremes.json --mode all`).
    *Expected:* conformity, decisive in this society, might be easier to
    measure. *Found:* the opposite: θ is the least identifiable of all runs
    (0.13 to 0.35; not identified from one survey anywhere), while water
    shares are well identified even from one survey (0.79). In very tight
    groups a minority practice disappears for any θ in the prior, so the data
    show that conformity blocks it but not how strongly (finding 33).
22. **(2c) How runs end in E1** (`--rho 0.7 --reps 25`, 0.2.3). *Found:* the
    October numbers reproduce; with every group seeded 94% of runs have
    settled by step 500, with single seeds 66%, and only a third of the
    sustained single-seed runs, most of the rest still rising at the
    threshold. Single-seed percentages are provisional in size; the
    2,000-step E1 already showed their signs hold (finding 34).
    (`docs/commons-results-followups.md`, part f)

Real groups (E2) were dropped from the roadmap in November 2026: describing
real communities needs data this project does not have. Scenario files
(`miras commons scenario`) and `miras commons identify` work for any groups
someone can describe.

## Next for miras.commons

### 1. Data that would recover conformity (0.2.4)

Findings 30 to 33: even ten survey waves with water records recover only
about 0.58 of the information about conformity, larger surveys barely help,
and where conformity is decisive it is least measurable. Conformity predicts copying the local
majority whatever the payoffs; payoff-based learning predicts copying those
who do better. A study can ask this directly ("whom did you learn it from?
did others in your group use it?"). To test such designs the model must
record each learning event: whether it was conformist or payoff-based, from
the learner's group or another, and whether the learner switched. Planned
for **0.2.4**:

- record learning events per group and step (counts only, so the random
  numbers and every result stay the same);
- a design `network` (and `panel+network`) in `miras commons identify`: the
  share of adopters in each group who name an in-group source, and the share
  who switched towards their group's majority;
- rerun the 0.2.3 studies with the new designs, above all the extreme
  groups, where surveys and records recover least about conformity
  (finding 33), and with more waves rather than more respondents
  (finding 32).

### 2. A longer default horizon?

Finding 34: a third of single-seed runs have not settled by step 500. The
2,000-step E1 kept every sign but moved the sizes (finding 27), and took
about four times as long. Options for 0.2.4: keep 500 steps and report the
settled share (as now), or make 2,000 the default for scenarios, where runs
are cheap. To be decided with the 0.2.4 runs.

### 3. Variants from the specification

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
