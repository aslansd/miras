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
   each group (at least five waves) together with water-delivery records by
   group. It recovers the water shares almost completely and conformity about
   half way, which is enough to tell "unequal shares hold the practice back"
   (γ well above 0) from "they do not" (γ near 0), but only roughly how
   strong conformity is.

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

- One society (the example scenario), one stress level (ρ = 0.7), 500 steps,
  100 respondents per group. More respondents or more waves would raise the
  contractions; `--respondents` and `--waves` test that.
- Priors matter: a narrower prior on λ₀ (if the value of water can be
  measured separately) would leave more information for θ.
- With fewer than about 10,000 simulations the richer designs (15 and 30
  numbers) gave unstable contractions and coverage as low as 0.72 (a
  3,000-simulation trial); 12,000 is the default.
- The model is a tool for thinking about mechanisms and about study design,
  not a model of any real basin.
