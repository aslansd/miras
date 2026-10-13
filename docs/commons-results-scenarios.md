# miras.commons results: scenarios (E2)

Four scenario runs, 50 runs per cell, severe stress (ρ = 0.7, so the commons
needs an overall adoption share A* = 0.75). Run with miras 0.2.1 (October
2026) and regenerated with 0.2.2 to add the adoption in each group; every
other number is identical. The groups are invented; they are not a model of
any real place or community. The curated findings are in `commons-findings.md`.

```
miras commons example > groups.json
miras commons scenario groups.json
miras commons scenario examples/extremes.json
miras commons scenario examples/extremes.json --off power_share
miras commons scenario examples/extremes.json --off tight_conformity
```

| file | group | size | tightness | altruism | parochialism | wealth | power | contact |
|---|---|---|---|---|---|---|---|---|
| example | Highland | 300 | 0.8 | 0.6 | 0.7 | 1.5 | 2.0 | 0.1 |
| example | Valley | 200 | 0.3 | 0.7 | 0.3 | 1.0 | 1.0 | 0.2 |
| example | Riverside | 150 | 0.5 | 0.4 | 0.5 | 0.6 | 0.5 | 0.3 |
| extremes | Dominant | 200 | 0.9 | 0.5 | 0.9 | 2.0 | 3.0 | 0.1 |
| extremes | Marginal | 200 | 0.1 | 0.5 | 0.1 | 0.5 | 0.3 | 0.1 |
| extremes | Open | 200 | 0.1 | 0.9 | 0.1 | 1.0 | 1.0 | 0.1 |
| extremes | Closed | 200 | 0.9 | 0.9 | 0.9 | 1.0 | 1.0 | 0.1 |

## The example scenario

### Seeded during plenty

| seed group | mode | sustained | mean adoption | reach | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| Valley | introduce | 0% | 0.32 ± 0.00 | 1.0 | 0.225 |
| (every group) | all | 0% | 0.29 ± 0.03 | 0.9 | 0.226 |
| Valley | originate | 0% | 0.26 ± 0.03 | 0.8 | 0.231 |
| Highland | introduce | 0% | 0.23 ± 0.04 | 0.7 | 0.234 |
| Highland | originate | 0% | 0.20 ± 0.04 | 0.6 | 0.236 |
| (no innovation) | none | 0% | 0.00 ± 0.00 | 0.0 | 0.259 |
| Riverside | originate | 0% | 0.00 ± 0.00 | 0.0 | 0.259 |
| Riverside | introduce | 0% | 0.00 ± 0.00 | 0.0 | 0.259 |

Adoption in each group (mean of the last 100 steps), seeded during plenty:

| seeding | Highland | Valley | Riverside | shortage | sustained |
| --- | --- | --- | --- | --- | --- |
| no innovation | 0.00 | 0.00 | 0.00 | 0.30 | 0% |
| every group | 0.02 | 0.89 | 0.04 | 0.20 | 0% |
| Highland originate | 0.02 | 0.61 | 0.02 | 0.24 | 0% |
| Highland introduce | 0.01 | 0.71 | 0.02 | 0.23 | 0% |
| Valley originate | 0.01 | 0.81 | 0.03 | 0.22 | 0% |
| Valley introduce | 0.01 | 0.99 | 0.03 | 0.20 | 0% |
| Riverside originate | 0.00 | 0.00 | 0.00 | 0.30 | 0% |
| Riverside introduce | 0.00 | 0.00 | 0.00 | 0.30 | 0% |

The commons needs an overall adoption share of 0.75 (A*); "sustained" also needs the shortage to stay below the collapse threshold.

### Seeded during scarcity

| seed group | mode | sustained | mean adoption | reach | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| (every group) | all | 0% | 0.33 ± 0.00 | 1.0 | 0.221 |
| Valley | introduce | 0% | 0.32 ± 0.00 | 1.0 | 0.225 |
| Highland | introduce | 0% | 0.32 ± 0.00 | 1.0 | 0.225 |
| Valley | originate | 0% | 0.32 ± 0.00 | 1.0 | 0.225 |
| Highland | originate | 0% | 0.31 ± 0.02 | 0.9 | 0.223 |
| (no innovation) | none | 0% | 0.00 ± 0.00 | 0.0 | 0.259 |
| Riverside | originate | 0% | 0.00 ± 0.00 | 0.0 | 0.259 |
| Riverside | introduce | 0% | 0.00 ± 0.00 | 0.0 | 0.259 |

Adoption in each group (mean of the last 100 steps), seeded during scarcity:

| seeding | Highland | Valley | Riverside | shortage | sustained |
| --- | --- | --- | --- | --- | --- |
| no innovation | 0.00 | 0.00 | 0.00 | 0.30 | 0% |
| every group | 0.03 | 0.99 | 0.04 | 0.19 | 0% |
| Highland originate | 0.03 | 0.93 | 0.03 | 0.20 | 0% |
| Highland introduce | 0.01 | 0.99 | 0.03 | 0.20 | 0% |
| Valley originate | 0.01 | 0.99 | 0.03 | 0.20 | 0% |
| Valley introduce | 0.01 | 0.99 | 0.03 | 0.20 | 0% |
| Riverside originate | 0.00 | 0.00 | 0.00 | 0.30 | 0% |
| Riverside introduce | 0.00 | 0.00 | 0.00 | 0.30 | 0% |

The commons needs an overall adoption share of 0.75 (A*); "sustained" also needs the shortage to stay below the collapse threshold.


## Extreme groups

### Seeded during plenty

| seed group | mode | sustained | mean adoption | reach | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| Open | introduce | 0% | 0.45 ± 0.00 | 2.0 | 0.182 |
| (every group) | all | 0% | 0.43 ± 0.01 | 2.0 | 0.181 |
| Open | originate | 0% | 0.40 ± 0.03 | 1.9 | 0.182 |
| Dominant | originate | 0% | 0.08 ± 0.05 | 0.4 | 0.200 |
| Dominant | introduce | 0% | 0.05 ± 0.04 | 0.2 | 0.202 |
| Closed | originate | 0% | 0.02 ± 0.03 | 0.1 | 0.204 |
| Closed | introduce | 0% | 0.02 ± 0.02 | 0.1 | 0.204 |
| Marginal | introduce | 0% | 0.01 ± 0.00 | 0.0 | 0.206 |
| Marginal | originate | 0% | 0.00 ± 0.00 | 0.0 | 0.205 |
| (no innovation) | none | 0% | 0.00 ± 0.00 | 0.0 | 0.205 |

Adoption in each group (mean of the last 100 steps), seeded during plenty:

| seeding | Dominant | Marginal | Open | Closed | shortage | sustained |
| --- | --- | --- | --- | --- | --- | --- |
| no innovation | 0.00 | 0.00 | 0.00 | 0.00 | 0.30 | 0% |
| every group | 0.00 | 0.74 | 0.99 | 0.00 | 0.15 | 0% |
| Dominant originate | 0.00 | 0.13 | 0.20 | 0.00 | 0.27 | 0% |
| Dominant introduce | 0.00 | 0.08 | 0.14 | 0.00 | 0.28 | 0% |
| Marginal originate | 0.00 | 0.01 | 0.00 | 0.00 | 0.30 | 0% |
| Marginal introduce | 0.00 | 0.02 | 0.00 | 0.00 | 0.30 | 0% |
| Open originate | 0.00 | 0.66 | 0.95 | 0.00 | 0.16 | 0% |
| Open introduce | 0.00 | 0.83 | 0.99 | 0.00 | 0.14 | 0% |
| Closed originate | 0.00 | 0.04 | 0.06 | 0.00 | 0.29 | 0% |
| Closed introduce | 0.00 | 0.02 | 0.04 | 0.00 | 0.29 | 0% |

The commons needs an overall adoption share of 0.75 (A*); "sustained" also needs the shortage to stay below the collapse threshold.

### Seeded during scarcity

| seed group | mode | sustained | mean adoption | reach | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| Open | introduce | 0% | 0.46 ± 0.00 | 2.0 | 0.182 |
| (every group) | all | 0% | 0.45 ± 0.01 | 2.0 | 0.181 |
| Open | originate | 0% | 0.44 ± 0.01 | 2.0 | 0.181 |
| Dominant | originate | 0% | 0.30 ± 0.05 | 1.4 | 0.187 |
| Dominant | introduce | 0% | 0.29 ± 0.06 | 1.3 | 0.190 |
| Closed | originate | 0% | 0.19 ± 0.06 | 0.8 | 0.194 |
| Closed | introduce | 0% | 0.16 ± 0.06 | 0.7 | 0.197 |
| Marginal | introduce | 0% | 0.01 ± 0.00 | 0.0 | 0.206 |
| Marginal | originate | 0% | 0.00 ± 0.00 | 0.0 | 0.205 |
| (no innovation) | none | 0% | 0.00 ± 0.00 | 0.0 | 0.205 |

Adoption in each group (mean of the last 100 steps), seeded during scarcity:

| seeding | Dominant | Marginal | Open | Closed | shortage | sustained |
| --- | --- | --- | --- | --- | --- | --- |
| no innovation | 0.00 | 0.00 | 0.00 | 0.00 | 0.30 | 0% |
| every group | 0.00 | 0.79 | 0.99 | 0.00 | 0.15 | 0% |
| Dominant originate | 0.00 | 0.48 | 0.73 | 0.00 | 0.20 | 0% |
| Dominant introduce | 0.00 | 0.52 | 0.65 | 0.00 | 0.20 | 0% |
| Marginal originate | 0.00 | 0.02 | 0.00 | 0.00 | 0.30 | 0% |
| Marginal introduce | 0.00 | 0.03 | 0.00 | 0.00 | 0.30 | 0% |
| Open originate | 0.00 | 0.75 | 0.99 | 0.00 | 0.15 | 0% |
| Open introduce | 0.00 | 0.83 | 0.99 | 0.00 | 0.14 | 0% |
| Closed originate | 0.00 | 0.29 | 0.45 | 0.00 | 0.24 | 0% |
| Closed introduce | 0.00 | 0.26 | 0.36 | 0.00 | 0.25 | 0% |

The commons needs an overall adoption share of 0.75 (A*); "sustained" also needs the shortage to stay below the collapse threshold.


## Extreme groups, equal water shares (--off power_share)

### Seeded during plenty

| seed group | mode | sustained | mean adoption | reach | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| (every group) | all | 0% | 0.49 ± 0.00 | 2.0 | 0.026 |
| Open | originate | 0% | 0.49 ± 0.00 | 2.0 | 0.026 |
| Marginal | introduce | 0% | 0.49 ± 0.00 | 2.0 | 0.026 |
| Open | introduce | 0% | 0.49 ± 0.00 | 2.0 | 0.026 |
| Marginal | originate | 0% | 0.33 ± 0.06 | 1.4 | 0.018 |
| Dominant | originate | 0% | 0.10 ± 0.05 | 0.4 | 0.005 |
| Dominant | introduce | 0% | 0.08 ± 0.05 | 0.3 | 0.004 |
| Closed | originate | 0% | 0.04 ± 0.04 | 0.2 | 0.002 |
| Closed | introduce | 0% | 0.03 ± 0.03 | 0.1 | 0.002 |
| (no innovation) | none | 0% | 0.00 ± 0.00 | 0.0 | 0.000 |

Adoption in each group (mean of the last 100 steps), seeded during plenty:

| seeding | Dominant | Marginal | Open | Closed | shortage | sustained |
| --- | --- | --- | --- | --- | --- | --- |
| no innovation | 0.00 | 0.00 | 0.00 | 0.00 | 0.30 | 0% |
| every group | 0.00 | 0.97 | 0.99 | 0.00 | 0.13 | 0% |
| Dominant originate | 0.00 | 0.19 | 0.20 | 0.00 | 0.27 | 0% |
| Dominant introduce | 0.00 | 0.16 | 0.16 | 0.00 | 0.27 | 0% |
| Marginal originate | 0.00 | 0.66 | 0.67 | 0.00 | 0.18 | 0% |
| Marginal introduce | 0.00 | 0.97 | 0.99 | 0.00 | 0.13 | 0% |
| Open originate | 0.00 | 0.97 | 0.99 | 0.00 | 0.13 | 0% |
| Open introduce | 0.00 | 0.97 | 0.99 | 0.00 | 0.13 | 0% |
| Closed originate | 0.00 | 0.08 | 0.08 | 0.00 | 0.29 | 0% |
| Closed introduce | 0.00 | 0.06 | 0.06 | 0.00 | 0.29 | 0% |

The commons needs an overall adoption share of 0.75 (A*); "sustained" also needs the shortage to stay below the collapse threshold.

### Seeded during scarcity

| seed group | mode | sustained | mean adoption | reach | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| Open | originate | 0% | 0.49 ± 0.00 | 2.0 | 0.026 |
| (every group) | all | 0% | 0.49 ± 0.00 | 2.0 | 0.026 |
| Marginal | introduce | 0% | 0.49 ± 0.00 | 2.0 | 0.026 |
| Marginal | originate | 0% | 0.49 ± 0.00 | 2.0 | 0.026 |
| Open | introduce | 0% | 0.49 ± 0.00 | 2.0 | 0.026 |
| Dominant | originate | 0% | 0.42 ± 0.05 | 1.7 | 0.022 |
| Dominant | introduce | 0% | 0.38 ± 0.06 | 1.6 | 0.020 |
| Closed | originate | 0% | 0.29 ± 0.07 | 1.2 | 0.016 |
| Closed | introduce | 0% | 0.25 ± 0.07 | 1.0 | 0.013 |
| (no innovation) | none | 0% | 0.00 ± 0.00 | 0.0 | 0.000 |

Adoption in each group (mean of the last 100 steps), seeded during scarcity:

| seeding | Dominant | Marginal | Open | Closed | shortage | sustained |
| --- | --- | --- | --- | --- | --- | --- |
| no innovation | 0.00 | 0.00 | 0.00 | 0.00 | 0.30 | 0% |
| every group | 0.00 | 0.97 | 0.99 | 0.00 | 0.13 | 0% |
| Dominant originate | 0.00 | 0.83 | 0.85 | 0.00 | 0.15 | 0% |
| Dominant introduce | 0.00 | 0.76 | 0.77 | 0.00 | 0.17 | 0% |
| Marginal originate | 0.00 | 0.97 | 0.99 | 0.00 | 0.13 | 0% |
| Marginal introduce | 0.00 | 0.97 | 0.99 | 0.00 | 0.13 | 0% |
| Open originate | 0.00 | 0.97 | 0.99 | 0.00 | 0.13 | 0% |
| Open introduce | 0.00 | 0.97 | 0.99 | 0.00 | 0.13 | 0% |
| Closed originate | 0.00 | 0.58 | 0.59 | 0.00 | 0.20 | 0% |
| Closed introduce | 0.00 | 0.49 | 0.49 | 0.00 | 0.21 | 0% |

The commons needs an overall adoption share of 0.75 (A*); "sustained" also needs the shortage to stay below the collapse threshold.


## Extreme groups, no conformity (--off tight_conformity)

### Seeded during plenty

| seed group | mode | sustained | mean adoption | reach | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| Closed | introduce | 86% | 0.66 ± 0.07 | 2.6 | 0.045 |
| Closed | originate | 22% | 0.17 ± 0.09 | 0.7 | 0.164 |
| (every group) | all | 4% | 0.74 ± 0.00 | 3.0 | 0.044 |
| Dominant | introduce | 2% | 0.74 ± 0.00 | 3.0 | 0.046 |
| Open | originate | 0% | 0.74 ± 0.00 | 3.0 | 0.046 |
| Open | introduce | 0% | 0.74 ± 0.00 | 3.0 | 0.046 |
| Dominant | originate | 0% | 0.50 ± 0.10 | 2.0 | 0.097 |
| Marginal | introduce | 0% | 0.01 ± 0.00 | 0.0 | 0.206 |
| Marginal | originate | 0% | 0.00 ± 0.00 | 0.0 | 0.205 |
| (no innovation) | none | 0% | 0.00 ± 0.00 | 0.0 | 0.205 |

Adoption in each group (mean of the last 100 steps), seeded during plenty:

| seeding | Dominant | Marginal | Open | Closed | shortage | sustained |
| --- | --- | --- | --- | --- | --- | --- |
| no innovation | 0.00 | 0.00 | 0.00 | 0.00 | 0.30 | 0% |
| every group | 1.00 | 0.93 | 0.99 | 0.05 | 0.00 | 4% |
| Dominant originate | 0.68 | 0.66 | 0.67 | 0.01 | 0.10 | 0% |
| Dominant introduce | 0.99 | 0.95 | 0.99 | 0.03 | 0.01 | 2% |
| Marginal originate | 0.00 | 0.01 | 0.00 | 0.00 | 0.30 | 0% |
| Marginal introduce | 0.00 | 0.03 | 0.00 | 0.00 | 0.30 | 0% |
| Open originate | 0.99 | 0.97 | 0.99 | 0.01 | 0.01 | 0% |
| Open introduce | 0.99 | 0.97 | 0.99 | 0.01 | 0.01 | 0% |
| Closed originate | 0.22 | 0.02 | 0.22 | 0.22 | 0.23 | 22% |
| Closed introduce | 0.86 | 0.09 | 0.85 | 0.86 | 0.04 | 86% |

The commons needs an overall adoption share of 0.75 (A*); "sustained" also needs the shortage to stay below the collapse threshold.

### Seeded during scarcity

| seed group | mode | sustained | mean adoption | reach | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| (every group) | all | 100% | 0.77 ± 0.00 | 3.0 | 0.019 |
| Closed | originate | 100% | 0.77 ± 0.00 | 3.0 | 0.019 |
| Closed | introduce | 100% | 0.77 ± 0.00 | 3.0 | 0.019 |
| Open | introduce | 8% | 0.74 ± 0.00 | 3.0 | 0.044 |
| Dominant | introduce | 6% | 0.74 ± 0.00 | 3.0 | 0.045 |
| Open | originate | 2% | 0.74 ± 0.00 | 3.0 | 0.046 |
| Dominant | originate | 0% | 0.74 ± 0.00 | 3.0 | 0.046 |
| Marginal | introduce | 0% | 0.01 ± 0.00 | 0.0 | 0.206 |
| Marginal | originate | 0% | 0.00 ± 0.00 | 0.0 | 0.205 |
| (no innovation) | none | 0% | 0.00 ± 0.00 | 0.0 | 0.205 |

Adoption in each group (mean of the last 100 steps), seeded during scarcity:

| seeding | Dominant | Marginal | Open | Closed | shortage | sustained |
| --- | --- | --- | --- | --- | --- | --- |
| no innovation | 0.00 | 0.00 | 0.00 | 0.00 | 0.30 | 0% |
| every group | 1.00 | 0.11 | 0.99 | 1.00 | 0.00 | 100% |
| Dominant originate | 1.00 | 0.97 | 0.99 | 0.01 | 0.01 | 0% |
| Dominant introduce | 1.00 | 0.92 | 0.99 | 0.07 | 0.00 | 6% |
| Marginal originate | 0.00 | 0.02 | 0.00 | 0.00 | 0.30 | 0% |
| Marginal introduce | 0.00 | 0.03 | 0.00 | 0.00 | 0.30 | 0% |
| Open originate | 0.99 | 0.95 | 0.99 | 0.03 | 0.01 | 2% |
| Open introduce | 1.00 | 0.90 | 0.99 | 0.09 | 0.00 | 8% |
| Closed originate | 0.99 | 0.10 | 0.99 | 1.00 | 0.00 | 100% |
| Closed introduce | 0.99 | 0.10 | 0.99 | 1.00 | 0.00 | 100% |

The commons needs an overall adoption share of 0.75 (A*); "sustained" also needs the shortage to stay below the collapse threshold.


