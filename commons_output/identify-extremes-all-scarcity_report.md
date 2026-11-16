# miras.commons identifiability

Groups: Dominant, Marginal, Open, Closed. Seeding: all (group Dominant) during scarcity. 500 steps; surveys of 100 people per group at steps 100, 200, 300, 400, 500.

Contraction: how much the data narrow the prior (0 = not at all, 1 = fully), averaged over test datasets. Coverage: how often the 90% interval contains the truth (should be near 0.90).

| design | theta contraction | gamma_share contraction | lambda0 contraction | findings |
| --- | --- | --- | --- | --- |
| survey | 0.13 | 0.79 | 0.40 | NOT_IDENTIFIED (theta) |
| survey+water | 0.14 | 0.94 | 0.63 | NOT_IDENTIFIED (theta) |
| panel | 0.29 | 0.86 | 0.57 | none |
| panel+water | 0.35 | 0.97 | 0.80 | none |

| design | theta coverage | gamma_share coverage | lambda0 coverage |
| --- | --- | --- | --- |
| survey | 0.88 | 0.93 | 0.92 |
| survey+water | 0.89 | 0.88 | 0.94 |
| panel | 0.93 | 0.91 | 0.93 |
| panel+water | 0.86 | 0.86 | 0.95 |

## survey: one survey at the end: adoption in each group

4 observed numbers.

- **NOT_IDENTIFIED** (warning) `theta`: The posterior for theta is close to its prior (contraction 0.13): these summaries carry little information about it, alone or in combination with other parameters.

## survey+water: the survey plus each group's water shortfall (records)

8 observed numbers.

- **NOT_IDENTIFIED** (warning) `theta`: The posterior for theta is close to its prior (contraction 0.14): these summaries carry little information about it, alone or in combination with other parameters.

## panel: the survey repeated at several waves

20 observed numbers.

No findings.

## panel+water: the panel plus each group's water shortfall before each wave

40 observed numbers.

No findings.

