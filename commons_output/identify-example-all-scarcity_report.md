# miras.commons identifiability

Groups: Highland, Valley, Riverside. Seeding: all (group Highland) during scarcity. 500 steps; surveys of 100 people per group at steps 100, 200, 300, 400, 500.

Contraction: how much the data narrow the prior (0 = not at all, 1 = fully), averaged over test datasets. Coverage: how often the 90% interval contains the truth (should be near 0.90).

| design | theta contraction | gamma_share contraction | lambda0 contraction | findings |
| --- | --- | --- | --- | --- |
| survey | 0.38 | 0.59 | 0.31 | NOT_IDENTIFIED (lambda0) |
| survey+water | 0.41 | 0.87 | 0.53 | none |
| panel | 0.57 | 0.69 | 0.42 | NOT_IDENTIFIED (lambda0) |
| panel+water | 0.62 | 0.97 | 0.65 | none |

| design | theta coverage | gamma_share coverage | lambda0 coverage |
| --- | --- | --- | --- |
| survey | 0.89 | 0.94 | 0.97 |
| survey+water | 0.91 | 0.93 | 0.95 |
| panel | 0.93 | 0.91 | 0.95 |
| panel+water | 0.92 | 0.89 | 0.93 |

## survey: one survey at the end: adoption in each group

3 observed numbers.

- **NOT_IDENTIFIED** (warning) `lambda0` *where gamma_share < 0.703*: The posterior for lambda0 is close to its prior (contraction 0.09 in this region): these summaries carry little information about it, alone or in combination with other parameters.

## survey+water: the survey plus each group's water shortfall (records)

6 observed numbers.

No findings.

## panel: the survey repeated at several waves

15 observed numbers.

- **NOT_IDENTIFIED** (warning) `lambda0` *where gamma_share < 0.703*: The posterior for lambda0 is close to its prior (contraction 0.15 in this region): these summaries carry little information about it, alone or in combination with other parameters.

## panel+water: the panel plus each group's water shortfall before each wave

30 observed numbers.

No findings.

