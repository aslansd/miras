# miras.commons: which field data can tell the mechanisms apart?

The first identifiability study of `miras.commons` (November 2026, miras
0.2.3). It answers roadmap step "Identifiability": the October runs found two
barriers to a water-saving practice, **conformity** in tight groups and
**unequal water shares** in a shortage, and showed that which one binds
depends on the calibration (findings 4, 6 and 25 in `commons-findings.md`).
To know which one holds the practice back in a real basin, a study would have
to estimate both. Which kinds of data could?

## What was simulated

- **Society**: the example scenario (`miras commons example`): Highland (300
  people, tight, powerful), Valley (200, loose, altruistic) and Riverside
  (150, poor, less altruistic), under severe stress (ρ = 0.7).
- **Three starting points**: the practice introduced into Valley at scarcity,
  introduced into Highland at scarcity, and seeded in every group at scarcity.
- **Parameters to recover**, drawn from these priors: the conformity exponent
  θ ~ Uniform(1, 3); the power weighting of water shares γ ~ Uniform(0, 2)
  (0 = equal shares, 1 = the default, 2 = strongly favouring the powerful);
  and, as a nuisance parameter the study also does not know, the value of
  saved water λ₀ ~ LogUniform(1, 16).
- **Four study designs**, all measured on the same simulated societies:
  - *survey*: one survey at the end (step 500) of 100 people per group,
    asking whether they use the practice (3 numbers);
  - *survey+water*: the survey plus each group's water shortfall over the
    last 50 steps, from delivery records (6 numbers);
  - *panel*: the survey repeated at steps 100, 200, 300, 400 and 500
    (15 numbers);
  - *panel+water*: the panel plus each group's shortfall before each wave
    (30 numbers).
- **Method**: 12,000 simulated studies per starting point; 100 of them in
  turn treated as the observed data and analysed with rejection ABC (5%
  acceptance, regression adjustment) against the rest. *Contraction* is how
  much the data narrow the prior (0 = not at all, 1 = completely), averaged
  over the 100 test datasets; *coverage* is how often the 90% interval
  contains the true value (it should be near 0.90).

Commands (about 13 minutes each on 2 cores; about 5 on 8):

```
miras commons identify --seed-group Valley
miras commons identify --seed-group Highland
miras commons identify --mode all
```

The full reports, with every finding and the region where it holds, are in
`commons_output/identify-example-*_report.md` (and `.json`).

## Results

Contraction (coverage of the 90% interval in brackets):

| starting point | design | conformity θ | water shares γ | value of water λ₀ |
| --- | --- | --- | --- | --- |
| Valley | survey | 0.25 (0.90) | 0.53 (0.92) | 0.30 (0.93) |
| Valley | survey+water | 0.32 (0.88) | **0.96** (0.91) | 0.52 (0.92) |
| Valley | panel | 0.38 (0.91) | 0.66 (0.88) | 0.41 (0.95) |
| Valley | panel+water | **0.51** (0.92) | **0.98** (0.87) | 0.61 (0.92) |
| Highland | survey | 0.23 (0.89) | 0.46 (0.89) | 0.23 (0.96) |
| Highland | survey+water | 0.32 (0.86) | **0.97** (0.88) | 0.39 (0.96) |
| Highland | panel | 0.44 (0.92) | 0.56 (0.86) | 0.34 (0.95) |
| Highland | panel+water | **0.49** (0.89) | **0.99** (0.88) | 0.52 (0.93) |
| every group | survey | 0.38 (0.89) | 0.59 (0.94) | 0.31 (0.97) |
| every group | survey+water | 0.41 (0.91) | **0.87** (0.93) | 0.53 (0.95) |
| every group | panel | 0.57 (0.93) | 0.69 (0.91) | 0.42 (0.95) |
| every group | panel+water | **0.62** (0.92) | **0.97** (0.89) | 0.65 (0.93) |

Coverage is between 0.86 and 0.97 everywhere, so the posteriors are honest
and the contractions can be compared.

`miras.identify` findings (all `NOT_IDENTIFIED`, warnings):

- **θ with one survey, wherever conformity is strong**: not identified where
  θ > 1.66 (Highland start) or θ > 2.38 (Valley start). A single snapshot
  cannot tell strong conformity from very strong conformity.
- **θ with a survey and water records, wherever shares are unequal**: not
  identified where γ > 0.70 (Valley and Highland starts). When the powerful
  group gets most of the water, adoption elsewhere stalls whatever the
  conformity, so the survey carries no trace of θ.
- **λ₀ wherever shares are nearly equal** (γ < 0.70), in most designs, never with
  panel+water (and with one survey from Highland, wherever θ > 1.66):
  with equal shares everyone feels the shortage alike, and a higher value of
  saved water raises adoption much as weaker conformity does.
- No finding for any design with panel and water records, and none for θ in
  any panel design or with every group seeded.

No `EQUIFINALITY` finding: no design confuses θ with γ along a trade-off
ridge. The two mechanisms leave different traces; the problem is that the
trace of conformity is faint.

## What this says

1. **Unequal water shares are easy to measure: use delivery records.** One
   survey of adoption recovers about half of the information about γ (0.46
   to 0.59); adding each group's shortfall from water-delivery records
   recovers nearly all of it (0.87 to 0.99), whatever the starting point.
   Who gets how much water in a shortage is close to being observed
   directly.
2. **Conformity is hard to measure, and needs repeated surveys.** One survey
   recovers a quarter of the information about θ when the practice starts in
   one group (0.23 to 0.25); five survey waves raise that to 0.38 to 0.44,
   and waves plus records to about one half (0.49 to 0.51). Conformity shows
   in how adoption *changes*: how fast a minority practice disappears and a
   majority one fixes, which one snapshot cannot see.
3. **Strong unequal shares hide conformity.** With a survey and water records
   θ is not identified where γ > 0.70: when shortages fall on the weak
   groups, adoption stalls there regardless of conformity. This is the data
   counterpart of finding 25 (with strong conformity, equal shares barely
   help): one barrier masks the other in the data as in the outcomes.
4. **Where the practice starts changes what can be learned.** Seeding every
   group gives conformity something to act on in every group, and θ is
   better recovered in every design (0.38 to 0.62, against 0.23 to 0.51).
   A study of a practice that started in one group sees conformity only
   where the practice reached.
5. **Recommended design, from these runs:** repeated surveys of adoption in
   each group (as many waves as can be afforded: ten recovered more than
   five, while four times as many respondents hardly helped; see the
   follow-ups below) together with water-delivery records by group. It recovers the water shares almost completely and conformity about
   half way, which is enough to tell "unequal shares hold the practice back"
   (γ well above 0) from "they do not" (γ near 0), but only roughly how
   strong conformity is.

## Follow-up runs: bigger surveys, more waves, another society

Three runs from the 0.2.3 roadmap (November 2026, on an 8-core Mac):

```
miras commons identify --seed-group Valley --respondents 400
miras commons identify --seed-group Valley --waves 10
miras commons identify examples/extremes.json --mode all
```

Reports: `commons_output/identify-example-introduce-Valley-scarcity-respondents400_report.md`,
`...-waves10_report.md` and `commons_output/identify-extremes-all-scarcity_report.md`.

**Bigger surveys and more waves**, Valley start (contraction; the first
column is the run above with 100 respondents and 5 waves):

| design | θ: 100 people, 5 waves | θ: 400 people | θ: 10 waves | γ: 100 / 400 / 10 waves |
| --- | --- | --- | --- | --- |
| survey | 0.25 | 0.27 | 0.25 | 0.53 / 0.55 / 0.53 |
| survey+water | 0.32 | 0.34 | 0.33 | 0.96 / 0.96 / 0.96 |
| panel | 0.38 | 0.41 | 0.49 | 0.66 / 0.67 / 0.69 |
| panel+water | 0.51 | 0.52 | 0.58 | 0.98 / 0.98 / 0.99 |

Coverage stays between 0.84 and 0.95. Four times as many respondents adds
only 0.01 to 0.03 to the contraction of θ: sampling people is not the limit,
the model's own randomness is (the same parameters give different
histories). Twice as many waves adds 0.07 to 0.11 to the panels: what
carries information about conformity is how adoption changes over time, and
watching it more often helps. With a survey and water records θ is now not
identified where γ > 1.33 (it was γ > 0.70 at 100 respondents), so larger
surveys shrink the region where unequal shares hide conformity, but do not
remove it.

**The extreme groups** (`examples/extremes.json`, every group seeded at
scarcity):

| design | θ | γ | λ₀ |
| --- | --- | --- | --- |
| survey | 0.13 | 0.79 | 0.40 |
| survey+water | 0.14 | 0.94 | 0.63 |
| panel | 0.29 | 0.86 | 0.57 |
| panel+water | 0.35 | 0.97 | 0.80 |

Coverage 0.86 to 0.95. Here conformity decides the outcome (the two tight
groups never adopt, findings 15 and 17), yet its exponent is the least
identifiable of all runs: with one survey it is not identified anywhere
(contraction 0.13), and even five waves with records recover only a third.
The likely reason: in groups this tight, conformity removes a minority
practice for any θ between 1 and 3, so the data show *that* conformity holds
but not how strong it is. Water shares, by contrast, are better identified than in the
example scenario, even from one survey (0.79): with four groups and very
unequal power, who goes short shows clearly in who adopts.

**What the follow-ups add**

6. **More waves help; more respondents barely do.** To learn about
   conformity, survey more often rather than more people.
7. **Where conformity is decisive, its strength cannot be measured.** In
   very tight groups the outcome is the same for any conformity exponent in
   the prior range, so a study can establish that conformity blocks the
   practice but not estimate θ; that needs groups or periods where the
   practice is a sizeable minority, or data on learning itself (next
   section).

## What would recover conformity better

Not yet tested, because the model does not yet record what such data would
measure:

- **Network questions**: whom people learned the practice from, and whether
  they changed to match their group. Conformity predicts copying the local
  majority regardless of payoffs; payoff-based learning predicts copying
  those who do better. The model would need to record each learning event
  (conformist or payoff-based, in-group or out-group), planned for 0.2.4.
- **Measures of social disapproval**: how strongly deviants are sanctioned
  (σ in the model). Sanctions are part of tightness, not of θ, so this would
  separate the two components of tightness rather than measure θ.

## Caveats

- Two societies (the example scenario and the extreme groups), one stress
  level (ρ = 0.7), 500 steps. Respondents (100, 400) and waves (5, 10) were
  varied for one starting point only.
- Priors matter: a narrower prior on λ₀ (if the value of water can be
  measured separately) would leave more information for θ.
- With fewer than about 10,000 simulations the richer designs (15 and 30
  numbers) gave unstable contractions and coverage as low as 0.72 (a
  3,000-simulation trial); 12,000 is the default.
- The model is a tool for thinking about mechanisms and about study design,
  not a model of any real basin.
