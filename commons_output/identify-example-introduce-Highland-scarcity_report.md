# miras.commons identifiability

Groups: Highland, Valley, Riverside. Seeding: introduce (group Highland) during scarcity. 500 steps; surveys of 100 people per group at steps 100, 200, 300, 400, 500.

Contraction: how much the data narrow the prior (0 = not at all, 1 = fully), averaged over test datasets. Coverage: how often the 90% interval contains the truth (should be near 0.90).

| design | theta contraction | gamma_share contraction | lambda0 contraction | findings |
| --- | --- | --- | --- | --- |
| survey | 0.23 | 0.46 | 0.23 | NOT_IDENTIFIED (theta); NOT_IDENTIFIED (lambda0) |
| survey+water | 0.32 | 0.97 | 0.39 | NOT_IDENTIFIED (theta); NOT_IDENTIFIED (lambda0) |
| panel | 0.44 | 0.56 | 0.34 | NOT_IDENTIFIED (lambda0) |
| panel+water | 0.49 | 0.99 | 0.52 | none |

| design | theta coverage | gamma_share coverage | lambda0 coverage |
| --- | --- | --- | --- |
| survey | 0.89 | 0.89 | 0.96 |
| survey+water | 0.86 | 0.88 | 0.96 |
| panel | 0.92 | 0.86 | 0.95 |
| panel+water | 0.89 | 0.88 | 0.93 |

## survey: one survey at the end: adoption in each group

3 observed numbers.

- **NOT_IDENTIFIED** (warning) `theta` *where theta > 1.66*: The posterior for theta is close to its prior (contraction 0.17 in this region): these summaries carry little information about it, alone or in combination with other parameters.
- **NOT_IDENTIFIED** (warning) `lambda0` *where theta > 1.66*: The posterior for lambda0 is close to its prior (contraction 0.19 in this region): these summaries carry little information about it, alone or in combination with other parameters.

## survey+water: the survey plus each group's water shortfall (records)

6 observed numbers.

- **NOT_IDENTIFIED** (warning) `theta` *where gamma_share > 0.703*: The posterior for theta is close to its prior (contraction 0.18 in this region): these summaries carry little information about it, alone or in combination with other parameters.
- **NOT_IDENTIFIED** (warning) `lambda0` *where gamma_share < 0.703*: The posterior for lambda0 is close to its prior (contraction 0.16 in this region): these summaries carry little information about it, alone or in combination with other parameters.

## panel: the survey repeated at several waves

15 observed numbers.

- **NOT_IDENTIFIED** (warning) `lambda0` *where gamma_share < 0.703*: The posterior for lambda0 is close to its prior (contraction 0.13 in this region): these summaries carry little information about it, alone or in combination with other parameters.

## panel+water: the panel plus each group's water shortfall before each wave

30 observed numbers.

No findings.

