# miras.commons: what the runs show

This is the curated summary of every `miras.commons` run so far (September and
October 2026; 23 full runs on an 8-core Mac with miras 0.2.0 and 0.2.1, which
give identical numbers for the same seed). The tables behind each statement
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

The severe-stress runs (1,952 cells × 50 runs) took 63 to 79 minutes each on
8 cores; a scenario takes under a minute.

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
    behind finding 4. Two things are new in this background and not yet
    explained: introducing the practice beats originating it by 12 to 14
    points at every level of parochialism (the outside subsidy and
    demonstrators are the likely reason; a knockout of that support would
    test it), and seeding at scarcity matters much more than elsewhere
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
    its parochial filter keeps it from copying anyone else: with the filter
    also switched off, Closed adopts from any starting point (a 6-run check).
18. **Where nothing holds a majority in place, adoption falls back to where
    saving stops paying.** In finding 17 adoption ends at 0.74 to 0.77
    against an A* of 0.75: once enough groups save water the shortage
    disappears, saving stops paying, and the group with the least to gain and
    the least norm pressure (Marginal: loose and poor) drops it. Whether the
    commons counts as "sustained" then depends on a few hundredths of
    adoption, and a run with almost no shortage can still be unsustainable,
    slowly emptying the store (Dominant introduced during plenty: shortage
    0.01, sustained 2%). E1 shows the same force at full scale: with every
    group seeded, mean adoption ends at 0.92 with sanctions, still 0.96
    without conformity, but 0.52 without sanctions (finding 5). Read scenario
    outcomes with the adoption in each group and the adoption gap, not only
    the sustained share.

## What this says, in one paragraph

Within this model, where to start matters less than who will refuse. A
resource-saving practice spreads from a loose group and fails in a tight one.
It reaches the other groups only if their members can see it pay, which
power-weighted water shares prevent for a weak pioneer and spare a powerful
group from. It is held above the threshold by sanctions, part of the same
tightness whose conformity blocks it at the start. When some groups are tight
and closed, no starting point is enough while their conformity holds; if it
weakens, the practice has to start inside the closed group, whose parochial
filter otherwise keeps it out. Sharing shortages equally helped in every run
set where it was tried.

## Caveats

- One calibration (A3). Roadmap step 4 (`--set`, new in 0.2.2) tests which
  conclusions survive moving the learning slope, the conformity exponent and
  the value of scarce water.
- Five groups of equal size in E1 and E1b; the scenarios vary sizes only in
  the example file.
- Findings 12 (introduction beats origination with tight neighbours), 17 (the
  role of the parochial filter) and 18 are from fewer runs or small checks and
  are flagged in `ROADMAP.md` for a proper test.
- The model is a tool for thinking about mechanisms, not a forecast for any
  real basin. Describing real communities needs the people who know them
  (ROADMAP step 3b).
