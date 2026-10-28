# miras.commons: what the runs show

This is the curated summary of every `miras.commons` run so far (September and
October 2026; 39 full runs on an 8-core Mac with miras 0.2.0, 0.2.1 and
0.2.2, which give identical numbers for the same seed and settings). The tables behind each statement
are in the `commons-results-*.md` files next to this one, and every one of
them can be regenerated from `commons_output/` with `miras commons analyze`.

**How to read the numbers.** "Sustained" means that over the last 100 of 500
steps, adoption stays at or above the share A* the commons needs
(A* = (1 − ρ)/δ, 0.75 under severe stress) and the shortage stays below the
collapse threshold. Percentages are averages over cells of 50-run means.
Severe stress is ρ = 0.7 (recharge covers 70% of demand without the
innovation), mild stress ρ = 0.85. All results depend on the calibration
(specification amendment A3): read the comparisons, not the exact
percentages. The groups in the scenarios are invented and are not a model of
any real place or community.

## The runs

| set | runs | what it asks | tables |
|---|---|---|---|
| pilot | 1 | which regimes occur | – |
| E1 | 1 (3,904 cells) | which seed group works best, in which mode and when | `commons-results-e1.md` |
| E3 knockouts | 6 | which mechanism carries each effect | `commons-results-knockouts.md` |
| E1b backgrounds | 7 | how much the other groups matter | `commons-results-backgrounds.md` |
| cross-checks | 2 | do the background effects run through the same mechanisms? | `commons-results-crosschecks.md` |
| replication | 2 | are the effects larger than Monte Carlo noise? | `commons-results-replication.md` |
| scenarios (E2) | 4 | invented groups, and four extreme groups with two knockouts | `commons-results-scenarios.md` |
| calibration sensitivity | 6 | do the conclusions survive other values of β_s, θ and λ₀? | `commons-results-sensitivity.md` |
| open questions | 5 | introduction support; the parochial filter; the threshold | `commons-results-open-questions.md` |
| follow-ups | 5 | calibration under mild stress; knockouts at θ = 2; a 3,000-step horizon | `commons-results-followups.md` |

The severe-stress runs (1,952 cells × 50 runs) took 63 to 79 minutes each on
8 cores, about half that with 25 runs per cell (the sensitivity runs); a
scenario takes under a minute.

## Findings

### Seeding and timing

1. **Under mild stress no single seed group sustains the commons** (0%, in
   every mode, timing and condition). Only seeding every group does, and only
   if it happens as shortages begin (63%) rather than during plenty (4%).
   With loose neighbours single seeds sometimes succeed (12 to 17%).
2. **Under severe stress timing matters less**: 93% vs 100% when every group
   is seeded, 21–23% vs 27–30% for single seeds (plenty vs scarcity).
3. **The best place to start under severe stress** is a loose, altruistic,
   mid-power group: sustained in about 95% of runs, originating or
   introduced. The replication (finding 13) shows this class of profile is
   robust, but the ranking within it is not: with each seed, 10 to 12
   profiles reach 94% or more (the best 95.5 to 96.5%), all of them loose and
   mid-power, and their order changes from seed to seed.

### What the seed group's attributes do, and through which mechanism

4. **Tight groups are poor starting points, because of conformity.** Sustained
   share by the seed group's tightness, low / mid / high: 45% / 30% / 1%.
   Without conformity: 38% / 42% / 32%. Without caution (less
   experimentation) or sanctions, the effect barely changes (−0.41, −0.40
   instead of −0.44). A rare new practice in a conformist group is pulled back
   to the majority before it can prove itself.
5. **Sanctions hold the finish.** With every group seeded under severe stress
   the commons is sustained in 96% of runs; without sanctions, in 9%. The norm
   enforcement that does not matter for a start protects a practice once it is
   the majority.
6. **Power works through the water, not prestige.** Sustained share by the
   seed group's power: 0% / 46% / 29%. Without prestige: unchanged (and the
   cell-by-cell differences are no larger than sampling noise). With equal
   shares in a shortage: 41% / 46% / 47%, and single-seed success rises from
   25% to 45%. When powerful groups get more water, a weak group's members
   look worse off and nobody copies them, while a powerful group is shielded
   from the shortage that would make the practice pay.
7. **Parochialism matters only for outsiders' practices, through ownership.**
   It lowers success when the practice is introduced (−0.14 from low to high)
   but not when it originates in the group (0.00). Without the ownership
   mechanism the effect nearly vanishes (−0.04) and introduction succeeds about
   twice as often (49% vs 25%).

### The other groups

8. **The neighbours matter more than the pioneer.** Single-seed success by the
   other four groups' character: loose 41%, middling 25%, more powerful 15%,
   poorer 4%, less altruistic 0%, tight 0%. With tight neighbours even seeding
   every group fails (0%); with poorer or less altruistic neighbours it
   succeeds about half the time (56%, 52%).
9. **Power is relative.** With more powerful neighbours only an equally
   powerful seed group ever succeeds (seed power low / mid / high:
   0% / 0% / 46%).
10. **All five background attributes low: nothing is sustained, but not because
    nothing spreads.** Adoption stalls short of the threshold (adoption gap
    −0.27, against −0.43 in the middling background).

### New in October 2026: cross-checks

11. **More powerful neighbours block a weaker pioneer through the water
    shares.** With equal shares in a shortage, single-seed success with
    powerful neighbours rises from 15% to 40% (originate) and 39%
    (introduce), and the effect of the seed group's own power falls from
    +0.46 to +0.12 (low / mid / high: 0% / 0% / 46% → 34% / 41% / 46%). The
    mechanism behind finding 9 is the one behind finding 6. Once power stops
    deciding who can start, tightness decides instead: its effect grows from
    −0.26 to −0.70 (loose pioneers 72%, tight 2%).
12. **Tight neighbours block the practice through conformity.** Without
    conformity, a tight background goes from 0% everywhere to 88% with every
    group seeded and 44% / 57% for single seeds (originate / introduce).
    Single seeds then do a little better than in the middling background
    without conformity (37%, 49%), though seeding every group does worse
    (88% against 97%). The mechanism behind finding 8's worst case is the one
    behind finding 4. Two things are new in this background: introducing the
    practice beats originating it by 12 to 14 points at every level of
    parochialism (explained by the support that comes with introduction,
    finding 20), and seeding at scarcity matters much more than elsewhere
    (+0.23 with every group seeded, +0.25 for origination).

### New in October 2026: replication

13. **The effects are not Monte Carlo noise.** Rerunning the severe-stress E1
    with seeds 2 and 3 reproduces every headline number: the references
    (0% / 96% / 25% / 25%) and the adoption gap (−0.43) exactly, and every
    attribute effect to within 0.01. Cell by cell, the sustained shares
    correlate at 0.993, and their mean absolute difference (0.020 and 0.021)
    is what sampling 50 runs per cell predicts (0.020). Individual cells can
    differ by up to 30 to 36 points, as expected for a few cells out of 1,952
    with 50 runs each: read cells as estimates with a ±14-point 95% interval,
    and averages over many cells as precise.

### New in October 2026: scenarios

14. **In the example scenario (Highland, Valley, Riverside) nothing is
    sustained, because two of the three groups refuse.** Valley, loose and
    altruistic, adopts whenever the practice reaches it (0.61 to 0.99).
    Highland, large, tight and powerful, does not (0.01 to 0.03) even when
    seeded: under rationing it barely feels the shortage, and its conformity
    pulls the practice back. Riverside, poor and less altruistic, does not
    either (0.02 to 0.04), and a seed there spreads nowhere. Overall adoption
    is at most 0.33 against the 0.75 needed.
15. **Four extreme groups: the tight groups decide the outcome.** With
    Dominant (tight, parochial, rich, very powerful), Marginal (loose, open,
    poor, weak), Open (loose, open, very altruistic) and Closed (tight,
    parochial, very altruistic), nothing is sustained in any seeding. The two
    tight groups never adopt; the two loose ones do when the practice starts
    in Open (Marginal 0.66 to 0.83, Open 0.95 to 0.99). Two of four equal
    groups adopting gives 0.5 at most, below the 0.75 needed: no choice of
    starting point can fix that.
16. **Equal shares let the weakest group pass the practice on, but do not
    reach the tight groups.** Without power-weighted shares, a seed in
    Marginal spreads to Open (from 0.02 to 0.97 when introduced), and the
    payoff inequality between groups falls from a Gini of 0.18 to 0.03; the
    tight groups still stay at 0, so nothing is sustained.
17. **Without conformity the commons can be sustained, and only by starting in
    the closed group.** Seeding every group or seeding Closed (originating or
    introduced) at scarcity sustains the commons in 100% of runs. Seeding
    Dominant or Open at scarcity reaches every group except Closed and fails
    (0 to 8%). During plenty only Closed works at all (introduced 86%,
    originating 22%; every group seeded 4%).
    Closed adopts a practice that starts with it, and the others copy it, but
    its parochial filter keeps it from copying anyone else (confirmed by
    finding 21).
18. **Where nothing holds a majority in place, adoption falls back to where
    saving stops paying.** In finding 17 adoption ends at 0.74 to 0.77
    against an A* of 0.75: once enough groups save water the shortage
    disappears, saving stops paying, and the group with the least to gain and
    the least norm pressure (Marginal: loose and poor) drops it. Whether the
    commons counts as "sustained" then depends on a few hundredths of
    adoption; the store drains, if at all, very slowly (finding 22). E1 shows the
    same force at full scale: with every
    group seeded, mean adoption ends at 0.92 with sanctions, still 0.96
    without conformity, but 0.52 without sanctions (finding 5). Read scenario
    outcomes with the adoption in each group and the adoption gap, not only
    the sustained share.

### New in October 2026, second round: calibration

19. **The conclusions survive the calibration; the success rates do not.**
    Moving each calibrated learning parameter of amendment A3 down and up
    (25 runs per cell, severe stress) changes how often a single seed
    succeeds, from 8% to 40%: the conformity exponent θ (1.2: 37 to 40%;
    2: 8 to 9%) and the value of saved water λ₀ (2: 8%; 8: 37 to 38%) matter
    most, the payoff-learning slope β_s little (5: 19%; 20: 27%; default
    25%). Every qualitative result holds in all six:
    - tightness hurts (sustained share by tightness always falls from low to
      high; effect −0.16 to −0.69), and the best starting groups are always
      loose and never weak;
    - a weak seed group almost never succeeds (0 to 2%), with one exception:
      when saved water is valued highly (λ₀ = 8) it succeeds 12 to 15% of
      the time; a mid-power group always does better than a powerful one;
    - parochialism matters only for an introduced practice (−0.04 to −0.20,
      against −0.01 to +0.02 for origination);
    - seeding at scarcity always beats seeding during plenty (+0.03 to
      +0.12 for single seeds);
    - seeding every group always does far better than any single seed (77 to
      100%).
    Where success is rare (θ = 2, λ₀ = 2) the effects are smaller in
    percentage points, but their signs and order are the same. Individual
    cells change much more than sampling explains (mean differences 0.04 to
    0.17), so the calibration decides *which* cells succeed, while the
    patterns across cells stay. The sensitivity runs used severe stress only.

### New in October 2026, second round: the open questions

20. **Introduction beats origination with tight neighbours because of the
    support that comes with it.** Without the subsidy and outside
    demonstrators (`--no-support`), introduction falls from 57% to 44%,
    exactly the origination rate, and cell by cell the two modes become
    indistinguishable (mean difference 0.024, the size of sampling noise).
    Support also halved the penalty for a tight seed group (tightness effect
    on introduction −0.10 with support, −0.22 without, as for origination)
    and lifted a mid-power seed from 70% to 95%. In the middling background
    the two modes tie on average (25% each), consistent with support being
    offset there by the ownership penalty that parochial groups attach to an
    outsider's practice (finding 7).
21. **The parochial filter is what keeps the closed group out.** In the
    extreme scenario without conformity, switching the filter off too lets
    Closed adopt from any starting point: at scarcity every seeding except
    Marginal's sustains the commons in 100% of runs (Marginal, too weak to
    be copied under power-weighted shares, still fails). During plenty an
    introduced practice still does better than an originated one (Closed:
    100% against 8%), again the support carrying the practice until it pays.
22. **Without conformity, adoption settles just below the threshold, at any
    level of stress.** In the extreme scenario without conformity:
    - at ρ = 0.75 the commons needs only 0.625, yet adoption stops at 0.56
      to 0.58: Dominant and Open adopt, Marginal stays at 0.24 and Closed out,
      with a 3% shortage left; seeding Closed brings Closed in but Open drops
      to 0.32. Nothing is sustained apart from Closed seeded (14% at
      scarcity, 70% introduced during plenty). The expected outcome
      (three adopting groups clear the lower threshold) did not happen:
      with less stress there is less to gain from saving, so adoption stops
      lower;
    - at ρ = 0.65 (A* = 0.875) adoption reaches 0.82 at best, with Marginal
      at 0.28 and a 4% shortage, and nothing is sustained;
    - at 1,500 steps instead of 500 (ρ = 0.7) the outcomes are the same
      (every group seeded at scarcity 100% → 92%; everything else
      unchanged). Where a small shortage is present it persists rather than
      growing. Where there is none but adoption is just under A*, the
      deficit is below 1% of the recharge, too small for 1,500 steps to tell
      a very slow drain from a steady state (3,000 steps at ρ = 0.75 show it
      is a drain, finding 26).
    Payoff-driven learning stops where saving just pays for itself, which
    leaves a small chronic shortage (consistent with the shortage-equals-cost
    equilibrium of verification check V5). Crossing the threshold needs something that
    holds adoption above what pays privately: in E1, the sanctions of tight
    groups (finding 5).

### New in October 2026, third round: follow-ups

23. **Mild stress became winnable when saved water was valued highly, not
    when conformity was weakened.**
    Under mild stress (ρ = 0.85) no single seed succeeds at the default
    calibration (0%). Weakening conformity (θ = 1.2) does not change that
    (0%; the best profile 4%), though seeding every group improves (34% →
    55%). Raising the value of saved water (λ₀ = 8) does: single seeds 34%
    (originate) and 40% (introduce), every group 89% (78% during plenty, 100%
    at scarcity). Under mild stress the barrier is that saving is worth too
    little, not that conformity is too strong. Once it is winnable, the same
    patterns appear as under severe stress: tightness hurts (−0.50 / −0.58),
    altruism helps (+0.41), parochialism matters only on introduction (−0.11
    against +0.01), scarcity beats plenty (+0.09 to +0.22), and a weak seed
    group does worst (13 to 17%, against 43 to 51% for mid or high power).
24. **The conformity exponent acts only through conformity.** With conformity
    switched off, θ = 2 and θ = 1.5 give the same results (single seeds 37% /
    49% in both; cells differ by 0.027 on average, the size of sampling noise
    for 25 against 50 runs). A consistency check of the model: θ has no other
    route into it.
25. **With strong conformity, equal water shares barely help.** At θ = 2,
    sharing shortages equally raises single-seed success only from 8–9% to
    12–13% (at the default: 25% to 45%), and the effect of the seed group's
    power does not shrink (+0.11 → +0.15); a weak seed group goes from 0% to
    4–5%. Switching conformity off, by contrast, lifts single seeds to 37% /
    49%. So the expected result ("the power effect shrinks with equal
    shares, as at the default") did not hold at θ = 2: when conformity stops
    almost every start, the water-share barrier has little left to block.
    Which barrier binds depends on the calibration; that each one is real
    does not (finding 19).
26. **Near the threshold, 500 steps is not long enough.** In the extreme
    scenario at ρ = 0.75 without conformity, running 3,000 steps instead of
    500 leaves every seeding with a lasting shortage unchanged (adoption
    0.56, shortage 3%), but moves the two cells that ended near A* = 0.625,
    from opposite sides, toward the same state. Seeding Closed at scarcity:
    sustained 14% → 64% (median adoption 0.57 → 0.66; Open's adoption rises
    from 0.27 to 0.59, presumably as the store slowly drains and saving
    starts to pay).
    Introducing into Closed during plenty: 70% → 30% (median 0.75 → 0.59;
    Open falls from 0.97 to 0.33). Payoff learning pulls adoption to the
    threshold from both sides (finding 22), and a sustained share measured
    near it after 500 steps is provisional.

## What this says, in one paragraph

Within this model, where to start matters less than who will refuse. A
resource-saving practice spreads from a loose group and fails in a tight one.
It reaches the other groups only if their members can see it pay, which
power-weighted water shares prevent for a weak pioneer and spare a powerful
group from. Left to what pays privately, adoption stops just short of what
the commons needs, with a small shortage left over; it is held
above the threshold by sanctions, part of the same tightness whose conformity
blocks it at the start. When some groups are tight and closed, no starting
point is enough while their conformity holds; if it weakens, the practice
has to start inside the closed group, whose parochial filter otherwise keeps
it out. Outside support (a subsidy and demonstrators) helps an introduced
practice through the period before it pays. Sharing shortages equally helped
in every run set where it was tried, though little when conformity is
strong. Under mild stress a single start worked only in the run where saved
water was valued highly. These conclusions held under every calibration
tried; the success rates, and which barrier binds, did not.

## Caveats

- The calibration (A3) changes the success rates a great deal (single seeds
  8 to 40% under severe stress, 0 to 40% under mild stress) but not the
  conclusions (findings 19 and 23). The sensitivity runs moved one parameter
  at a time; under mild stress only θ = 1.2 and λ₀ = 8 were tried.
- Five groups of equal size in E1 and E1b; the scenarios vary sizes only in
  the example file.
- "Sustained" is strict: a run that ends just below A* with a 1 to 4%
  shortage counts as not sustained (finding 22), and near the threshold the
  outcome after 500 steps can still change (finding 26). Read it with the
  adoption gap, the shortage and the adoption in each group.
- Findings 21, 22 and 26 come from one invented four-group scenario; they show
  what the model can do, not how common it is.
- The model is a tool for thinking about mechanisms, not a forecast for any
  real basin. Describing real communities needs the people who know them
  (ROADMAP, real groups).
