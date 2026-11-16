# miras.commons identifiability

Groups: Highland, Valley, Riverside. Seeding: introduce (group Valley) during scarcity. 500 steps; surveys of 100 people per group at steps 50, 100, 150, 200, 250, 300, 350, 400, 450, 500.

Contraction: how much the data narrow the prior (0 = not at all, 1 = fully), averaged over test datasets. Coverage: how often the 90% interval contains the truth (should be near 0.90).

| design | theta contraction | gamma_share contraction | lambda0 contraction | findings |
| --- | --- | --- | --- | --- |
| survey | 0.25 | 0.53 | 0.29 | NOT_IDENTIFIED (theta); NOT_IDENTIFIED (lambda0) |
| survey+water | 0.33 | 0.96 | 0.53 | NOT_IDENTIFIED (theta) |
| panel | 0.49 | 0.69 | 0.45 | NOT_IDENTIFIED (lambda0) |
| panel+water | 0.58 | 0.99 | 0.66 | none |

| design | theta coverage | gamma_share coverage | lambda0 coverage |
| --- | --- | --- | --- |
| survey | 0.90 | 0.93 | 0.94 |
| survey+water | 0.91 | 0.89 | 0.92 |
| panel | 0.85 | 0.91 | 0.94 |
| panel+water | 0.92 | 0.84 | 0.92 |

## survey: one survey at the end: adoption in each group

3 observed numbers.

- **NOT_IDENTIFIED** (warning) `theta` *where theta > 2.38*: The posterior for theta is close to its prior (contraction 0.15 in this region): these summaries carry little information about it, alone or in combination with other parameters.
- **NOT_IDENTIFIED** (warning) `lambda0` *where gamma_share < 0.703*: The posterior for lambda0 is close to its prior (contraction 0.11 in this region): these summaries carry little information about it, alone or in combination with other parameters.

## survey+water: the survey plus each group's water shortfall (records)

6 observed numbers.

- **NOT_IDENTIFIED** (warning) `theta` *where gamma_share > 1.33*: The posterior for theta is close to its prior (contraction 0.12 in this region): these summaries carry little information about it, alone or in combination with other parameters.

## panel: the survey repeated at several waves

30 observed numbers.

- **NOT_IDENTIFIED** (warning) `lambda0` *where gamma_share < 0.703*: The posterior for lambda0 is close to its prior (contraction 0.15 in this region): these summaries carry little information about it, alone or in combination with other parameters.

## panel+water: the panel plus each group's water shortfall before each wave

60 observed numbers.

No findings.

