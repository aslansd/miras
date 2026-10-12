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

**The example scenario** (`miras commons example`: Highland, Valley,
Riverside, at ρ = 0.7) sustained the commons in 0% of runs for every seeding,
including seeding every group; mean adoption stayed near 0.33 against the
0.75 needed. Adoption per group shows why: only Valley keeps the practice
(about 0.99). Highland, large, tight and powerful, barely feels the shortage
under rationing and drops the practice even when seeded (about 0.03).
Riverside, poor and less altruistic, drops it too (about 0.05) and cannot pass
it on when seeded. As in the one-attribute backgrounds, the groups that refuse
decide the outcome more than the group where the practice starts.

## Next for miras.commons

All of steps 1 to 3 need no new code (step 3 adds two example files,
`examples/extremes.json` and `examples/per_group.py`).

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

Every result so far comes from one master seed. Rerun the severe-stress E1
with a second seed, into its own folder (the seed is part of the checkpoint
key but not of the output file names, so a separate folder keeps the two runs
apart). About 50 minutes on 8 cores:

```
miras commons e1 --rho 0.7 --seed 2 --cores 8 --outdir commons_output_seed2
miras commons analyze commons_output/e1_summary.csv \
    commons_output_seed2/e1-rho0.7_summary.csv --rho 0.7 --out replication.md
```

The first file (seed 1, all conditions) is filtered to ρ = 0.7 by `--rho`, so
the two columns of the report compare like with like. Check that each seed-1
result comes back in the same direction:

| result (ρ = 0.7, seed 1) | value |
|---|---|
| references: one seed group / every group seeded | 21–30% / 93–100% sustained |
| tightness of the seed group, low / mid / high | 45 / 30 / 1% |
| power of the seed group, low / mid / high | 0 / 46 / 29% |
| parochialism, effect on introduction / origination | −0.14 / about 0 |
| neighbours (from E1b), loose / tight | 41% / 0% |

Differences of 3 to 5 percentage points are Monte Carlo noise. A change of
direction (for example high tightness doing better than low) would be a red
flag. For more confidence, add `--seed 3` into a third folder (another 50
minutes).

### 3. Scenarios (E2): an extreme-case stress test first, then real groups

**3a. Extreme groups.** Before describing real groups, run a scenario whose
groups sit at the extremes of the attributes. This is a test of the model, not
a picture of any real basin: with each mechanism made large, the result should
be explainable from what E1 found, and a result that cannot be explained is a
finding too. Give such groups abstract names and never read them as real
communities.

`examples/extremes.json` has four groups of equal size (200 each, so size does
not blur the comparison), all with contact 0.1, at ρ = 0.7 and both timings:

| group | tightness | altruism | parochialism | wealth | power |
|---|---|---|---|---|---|
| Dominant | 0.9 | 0.5 | 0.9 | 2.0 | 3.0 |
| Marginal | 0.1 | 0.5 | 0.1 | 0.5 | 0.3 |
| Open | 0.1 | 0.9 | 0.1 | 1.0 | 1.0 |
| Closed | 0.9 | 0.9 | 0.9 | 1.0 | 1.0 |

Run it as it is and with the two mechanisms E1 found decisive switched off
(each run takes a couple of minutes: 20 cells × 50 runs):

```
miras commons scenario examples/extremes.json --cores 8
miras commons scenario examples/extremes.json --cores 8 --off power_share
miras commons scenario examples/extremes.json --cores 8 --off tight_conformity
```

The scenario report gives only the seed group and "everyone else". The
explanation is in which groups hold out, so also run the helper
`examples/per_group.py`, which prints adoption in each group, the shortage
and the number of sustained runs for every seeding:

```
python examples/per_group.py examples/extremes.json
python examples/per_group.py examples/extremes.json --off power_share
python examples/per_group.py examples/extremes.json --off tight_conformity
python examples/per_group.py examples/extremes.json --timing plenty
```

*Expected, from a small test run (10 runs per cell, to be confirmed at 50):*

- **As it is:** 0% sustained for every seeding, including every group seeded.
  The two loose groups (Marginal, Open) adopt and the two tight groups
  (Dominant, Closed) stay at 0. Half the population adopting cannot reach the
  0.75 the water balance needs at ρ = 0.7, so this is arithmetic as much as
  seeding: the tight groups have to be won over.
- **Without conformity:** both tight groups adopt and the commons is
  sustained when every group is seeded or when the practice is introduced
  into Closed (6 of 6 runs each). Seeded in Dominant or Open, the practice reaches every group except
  Closed and falls just short. Marginal, the poorest group, largely stops
  paying once the shortage is gone.
- **With equal water shares:** a seed in Marginal now spreads to Open, which
  it cannot do with power-weighted shares, as in E1 (a weak seed group is not
  copied while shares are unequal).

Useful follow-ups on the same file: `"resource": {"rho": 0.85}` (mild
stress), unequal sizes, and higher contact for the tight groups.

**3b. Real groups.** `miras commons example > groups.json`, then describe the
groups of a real case: sizes and rough positions on each attribute. For a case
such as the Lake Urmia basin, these positions should come from people who know
the communities, or from published survey measures, never from assigning
traits to ethnic or religious groups from outside. The result is specific to
that description: which group to seed, in which mode, and when. Run
`per_group.py` on it as well, and compare the pattern with the extreme case.

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
