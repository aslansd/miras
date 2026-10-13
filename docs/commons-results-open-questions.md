# miras.commons results: open questions from the October runs

Three questions left open by the cross-checks and the extreme-group
scenarios (October 2026, miras 0.2.2, severe stress ρ = 0.7 unless stated).
The curated findings are in `commons-findings.md`. Regenerate with:

```
miras commons analyze commons_output/e1b-tightness-high-rho0.7-off-tight_conformity_summary.csv \
    commons_output/e1b-tightness-high-rho0.7-off-tight_conformity-nosupport_summary.csv --rho 0.7
```

and the scenario reports in `commons_output/scenario-extremes-off-tight_conformity-*_report.md`.
The groups are invented (see `commons-results-scenarios.md` for their attributes).

## (a) Why does introduction beat origination with tight neighbours?

`miras commons e1 --rho 0.7 --background tightness=high --off tight_conformity --no-support`,
compared with the same run with support.


Runs: `e1b-tightness-high-rho0.7-off-tight_conformity`, `e1b-tightness-high-rho0.7-off-tight_conformity-nosupport`. Numbers are averages over cells of 50-run means (see each summary's `reps`); they are conditional on the model's calibration (specification amendment A3).

### Overview

Share of runs that sustain the commons, by seeding mode (single-seed modes averaged over all seed profiles), and the mean adoption gap of single seeds (adoption minus the share A* the commons needs; negative = short of it).

| run | rho | no innovation | every group | originate | introduce | best single profile | adoption gap (single seeds) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| e1b-tightness-high-rho0.7-off-tight_conformity | 0.7 | 0% | 88% | 44% | 57% | 100% | -0.24 |
| e1b-tightness-high-rho0.7-off-tight_conformity-nosupport | 0.7 | 0% | 88% | 44% | 44% | 100% | -0.31 |

### Details for `e1b-tightness-high-rho0.7-off-tight_conformity`

#### Main effects of the seed group's attributes (e1b-tightness-high-rho0.7-off-tight_conformity, rho = 0.7)

Mean over the other attributes and over the conditions in the file. Sustained share / mean adoption.

| attribute | mode | low | mid | high | high - low (sustained) |
| --- | --- | --- | --- | --- | --- |
| tightness | originate | 54% / 0.53 | 47% / 0.48 | 32% / 0.31 | -0.22 |
| tightness | introduce | 61% / 0.59 | 59% / 0.61 | 51% / 0.52 | -0.10 |
| altruism | originate | 34% / 0.31 | 45% / 0.45 | 52% / 0.55 | +0.18 |
| altruism | introduce | 47% / 0.44 | 56% / 0.58 | 67% / 0.70 | +0.19 |
| parochialism | originate | 44% / 0.44 | 44% / 0.44 | 44% / 0.44 | -0.00 |
| parochialism | introduce | 58% / 0.58 | 57% / 0.58 | 56% / 0.57 | -0.02 |
| wealth | originate | 36% / 0.35 | 43% / 0.45 | 53% / 0.52 | +0.18 |
| wealth | introduce | 48% / 0.49 | 56% / 0.58 | 66% / 0.65 | +0.17 |
| power | originate | 1% / 0.11 | 70% / 0.62 | 61% / 0.59 | +0.61 |
| power | introduce | 6% / 0.20 | 95% / 0.84 | 70% / 0.69 | +0.64 |

#### Where adoption happens, by the seed group's power (e1b-tightness-high-rho0.7-off-tight_conformity, rho = 0.7, originate)

| seed power | seed-group adoption | other groups' adoption | groups reached | sustained | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| 0.5 | 0.51 | 0.01 | 0.6 | 1% | 0.070 |
| 1 | 0.34 | 0.68 | 3.1 | 70% | 0.009 |
| 2 | 0.27 | 0.67 | 3.0 | 61% | 0.036 |

#### Sustained share by seed tightness and power (e1b-tightness-high-rho0.7-off-tight_conformity, rho = 0.7, originate)

| tightness / power | 0.5 | 1 | 2 |
| --- | --- | --- | --- |
| 0.1 | 2% | 90% | 69% |
| 0.5 | 0% | 72% | 68% |
| 0.9 | 0% | 47% | 48% |

#### Introduce minus originate, by the seed group's parochialism (e1b-tightness-high-rho0.7-off-tight_conformity, rho = 0.7)

| parochialism | sustained | mean adoption |
| --- | --- | --- |
| 0.1 | +0.14 | +0.15 |
| 0.5 | +0.13 | +0.14 |
| 0.9 | +0.12 | +0.12 |

#### Seeding at scarcity minus during plenty (e1b-tightness-high-rho0.7-off-tight_conformity, rho = 0.7)

| mode | sustained | mean adoption |
| --- | --- | --- |
| all | +0.23 | +0.24 |
| originate | +0.25 | +0.25 |
| introduce | +0.09 | +0.09 |

#### Best seed groups (e1b-tightness-high-rho0.7-off-tight_conformity, rho = 0.7; mean over conditions)

| tightness | altruism | parochialism | wealth | power | mode | sustained | mean adoption |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.5 | 0.1 | 0.1 | 2 | 1 | introduce | 100% | 0.99 |
| 0.5 | 0.5 | 0.1 | 2 | 1 | introduce | 100% | 0.99 |
| 0.5 | 0.9 | 0.1 | 2 | 1 | introduce | 100% | 0.99 |
| 0.5 | 0.9 | 0.1 | 2 | 2 | introduce | 100% | 0.99 |
| 0.5 | 0.1 | 0.5 | 1 | 1 | introduce | 100% | 0.99 |

### Comparison across runs

Effect of each seed attribute (high minus low) on the sustained share, per run. An effect that shrinks or vanishes when a mechanism is switched off (E3) is carried by that mechanism; one that survives a different background (E1b) does not depend on it.

#### rho = 0.7, originate

| attribute | e1b-tightness-high-rho0.7-off-tight_conformity | e1b-tightness-high-rho0.7-off-tight_conformity-nosupport |
| --- | --- | --- |
| tightness | -0.22 | -0.22 |
| altruism | +0.18 | +0.18 |
| parochialism | -0.00 | -0.00 |
| wealth | +0.18 | +0.18 |
| power | +0.61 | +0.61 |
| *power, low / mid / high* | 1% / 70% / 61% | 1% / 70% / 61% |

Effect (high minus low) on mean adoption:

| attribute | e1b-tightness-high-rho0.7-off-tight_conformity | e1b-tightness-high-rho0.7-off-tight_conformity-nosupport |
| --- | --- | --- |
| tightness | -0.22 | -0.22 |
| altruism | +0.24 | +0.24 |
| parochialism | +0.01 | +0.01 |
| wealth | +0.17 | +0.17 |
| power | +0.49 | +0.49 |

#### rho = 0.7, introduce

| attribute | e1b-tightness-high-rho0.7-off-tight_conformity | e1b-tightness-high-rho0.7-off-tight_conformity-nosupport |
| --- | --- | --- |
| tightness | -0.10 | -0.22 |
| altruism | +0.19 | +0.18 |
| parochialism | -0.02 | -0.00 |
| wealth | +0.17 | +0.17 |
| power | +0.64 | +0.61 |
| *power, low / mid / high* | 6% / 95% / 70% | 0% / 70% / 62% |

Effect (high minus low) on mean adoption:

| attribute | e1b-tightness-high-rho0.7-off-tight_conformity | e1b-tightness-high-rho0.7-off-tight_conformity-nosupport |
| --- | --- | --- |
| tightness | -0.08 | -0.21 |
| altruism | +0.27 | +0.24 |
| parochialism | -0.02 | -0.00 |
| wealth | +0.16 | +0.17 |
| power | +0.49 | +0.49 |

### Cell-by-cell agreement with the first run

Over the cells each run shares with `e1b-tightness-high-rho0.7-off-tight_conformity`. For a replication (same cells, another seed) the mean absolute difference in the sustained share should be close to the value expected from sampling alone; the effects in the tables above average over many cells and so vary much less.

| run | shared cells | correlation, sustained | correlation, adoption | mean abs. difference, sustained | expected from sampling | largest difference |
| --- | --- | --- | --- | --- | --- | --- |
| e1b-tightness-high-rho0.7-off-tight_conformity-nosupport | 1952 | 0.906 | 0.886 | 0.069 | 0.023 | 100% |


## (b) The parochial filter: extreme groups, no conformity, no parochial filter

`miras commons scenario examples/extremes.json --off tight_conformity,outgroup_filter`

### Seeded during plenty

| seed group | mode | sustained | mean adoption | reach | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| (every group) | all | 100% | 0.78 ± 0.00 | 3.0 | 0.018 |
| Open | originate | 100% | 0.77 ± 0.00 | 3.0 | 0.018 |
| Dominant | introduce | 100% | 0.77 ± 0.00 | 3.0 | 0.018 |
| Open | introduce | 100% | 0.77 ± 0.00 | 3.0 | 0.018 |
| Closed | introduce | 100% | 0.77 ± 0.00 | 3.0 | 0.018 |
| Dominant | originate | 78% | 0.60 ± 0.09 | 2.3 | 0.059 |
| Closed | originate | 8% | 0.06 ± 0.06 | 0.2 | 0.190 |
| Marginal | introduce | 0% | 0.01 ± 0.00 | 0.0 | 0.206 |
| Marginal | originate | 0% | 0.00 ± 0.00 | 0.0 | 0.205 |
| (no innovation) | none | 0% | 0.00 ± 0.00 | 0.0 | 0.205 |

Adoption in each group (mean of the last 100 steps), seeded during plenty:

| seeding | Dominant | Marginal | Open | Closed | shortage | sustained |
| --- | --- | --- | --- | --- | --- | --- |
| no innovation | 0.00 | 0.00 | 0.00 | 0.00 | 0.30 | 0% |
| every group | 1.00 | 0.12 | 0.99 | 1.00 | 0.00 | 100% |
| Dominant originate | 0.78 | 0.09 | 0.77 | 0.78 | 0.07 | 78% |
| Dominant introduce | 0.99 | 0.12 | 0.99 | 0.99 | 0.00 | 100% |
| Marginal originate | 0.00 | 0.01 | 0.00 | 0.00 | 0.30 | 0% |
| Marginal introduce | 0.00 | 0.03 | 0.00 | 0.00 | 0.30 | 0% |
| Open originate | 0.99 | 0.12 | 0.99 | 0.99 | 0.00 | 100% |
| Open introduce | 0.99 | 0.11 | 0.99 | 0.99 | 0.00 | 100% |
| Closed originate | 0.08 | 0.01 | 0.08 | 0.08 | 0.28 | 8% |
| Closed introduce | 0.99 | 0.11 | 0.99 | 0.99 | 0.00 | 100% |

The commons needs an overall adoption share of 0.75 (A*); "sustained" also needs the shortage to stay below the collapse threshold.

### Seeded during scarcity

| seed group | mode | sustained | mean adoption | reach | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| (every group) | all | 100% | 0.78 ± 0.00 | 3.0 | 0.018 |
| Dominant | originate | 100% | 0.77 ± 0.00 | 3.0 | 0.018 |
| Open | originate | 100% | 0.77 ± 0.00 | 3.0 | 0.018 |
| Closed | originate | 100% | 0.77 ± 0.00 | 3.0 | 0.018 |
| Open | introduce | 100% | 0.77 ± 0.00 | 3.0 | 0.018 |
| Closed | introduce | 100% | 0.77 ± 0.00 | 3.0 | 0.018 |
| Dominant | introduce | 100% | 0.77 ± 0.00 | 3.0 | 0.019 |
| Marginal | introduce | 0% | 0.01 ± 0.00 | 0.0 | 0.206 |
| Marginal | originate | 0% | 0.01 ± 0.00 | 0.0 | 0.205 |
| (no innovation) | none | 0% | 0.00 ± 0.00 | 0.0 | 0.205 |

Adoption in each group (mean of the last 100 steps), seeded during scarcity:

| seeding | Dominant | Marginal | Open | Closed | shortage | sustained |
| --- | --- | --- | --- | --- | --- | --- |
| no innovation | 0.00 | 0.00 | 0.00 | 0.00 | 0.30 | 0% |
| every group | 1.00 | 0.12 | 0.99 | 1.00 | 0.00 | 100% |
| Dominant originate | 1.00 | 0.12 | 0.99 | 0.99 | 0.00 | 100% |
| Dominant introduce | 0.99 | 0.11 | 0.99 | 0.99 | 0.00 | 100% |
| Marginal originate | 0.00 | 0.02 | 0.00 | 0.00 | 0.30 | 0% |
| Marginal introduce | 0.00 | 0.03 | 0.00 | 0.00 | 0.30 | 0% |
| Open originate | 0.99 | 0.12 | 0.99 | 1.00 | 0.00 | 100% |
| Open introduce | 1.00 | 0.11 | 0.99 | 0.99 | 0.00 | 100% |
| Closed originate | 0.99 | 0.12 | 0.99 | 1.00 | 0.00 | 100% |
| Closed introduce | 0.99 | 0.11 | 0.99 | 1.00 | 0.00 | 100% |

The commons needs an overall adoption share of 0.75 (A*); "sustained" also needs the shortage to stay below the collapse threshold.


## (c) The threshold: extreme groups, no conformity, ρ = 0.65 (A* = 0.875)

`miras commons scenario examples/extremes.json --off tight_conformity --set resource.rho=0.65`

### Seeded during plenty

| seed group | mode | sustained | mean adoption | reach | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| Open | introduce | 0% | 0.78 ± 0.01 | 3.0 | 0.076 |
| Open | originate | 0% | 0.78 ± 0.01 | 3.0 | 0.078 |
| (every group) | all | 0% | 0.77 ± 0.01 | 3.0 | 0.085 |
| Dominant | introduce | 0% | 0.75 ± 0.01 | 3.0 | 0.118 |
| Closed | introduce | 0% | 0.73 ± 0.07 | 2.7 | 0.043 |
| Dominant | originate | 0% | 0.58 ± 0.09 | 2.3 | 0.148 |
| Closed | originate | 0% | 0.34 ± 0.11 | 1.3 | 0.142 |
| Marginal | introduce | 0% | 0.00 ± 0.00 | 0.0 | 0.229 |
| Marginal | originate | 0% | 0.00 ± 0.00 | 0.0 | 0.228 |
| (no innovation) | none | 0% | 0.00 ± 0.00 | 0.0 | 0.228 |

Adoption in each group (mean of the last 100 steps), seeded during plenty:

| seeding | Dominant | Marginal | Open | Closed | shortage | sustained |
| --- | --- | --- | --- | --- | --- | --- |
| no innovation | 0.00 | 0.00 | 0.00 | 0.00 | 0.35 | 0% |
| every group | 1.00 | 0.71 | 0.99 | 0.39 | 0.06 | 0% |
| Dominant originate | 0.78 | 0.76 | 0.77 | 0.01 | 0.14 | 0% |
| Dominant introduce | 0.99 | 0.92 | 0.99 | 0.09 | 0.07 | 0% |
| Marginal originate | 0.00 | 0.00 | 0.00 | 0.00 | 0.35 | 0% |
| Marginal introduce | 0.00 | 0.01 | 0.00 | 0.00 | 0.35 | 0% |
| Open originate | 0.99 | 0.65 | 0.99 | 0.46 | 0.06 | 0% |
| Open introduce | 0.99 | 0.64 | 0.99 | 0.48 | 0.06 | 0% |
| Closed originate | 0.42 | 0.12 | 0.42 | 0.42 | 0.22 | 0% |
| Closed introduce | 0.90 | 0.25 | 0.89 | 0.90 | 0.07 | 0% |

The commons needs an overall adoption share of 0.87 (A*); "sustained" also needs the shortage to stay below the collapse threshold.

### Seeded during scarcity

| seed group | mode | sustained | mean adoption | reach | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| (every group) | all | 0% | 0.82 ± 0.00 | 3.0 | 0.022 |
| Closed | introduce | 0% | 0.82 ± 0.00 | 3.0 | 0.022 |
| Closed | originate | 0% | 0.82 ± 0.00 | 3.0 | 0.022 |
| Open | originate | 0% | 0.79 ± 0.01 | 3.0 | 0.063 |
| Open | introduce | 0% | 0.78 ± 0.01 | 3.0 | 0.067 |
| Dominant | introduce | 0% | 0.76 ± 0.01 | 3.0 | 0.101 |
| Dominant | originate | 0% | 0.74 ± 0.00 | 3.0 | 0.126 |
| Marginal | introduce | 0% | 0.00 ± 0.00 | 0.0 | 0.229 |
| Marginal | originate | 0% | 0.00 ± 0.00 | 0.0 | 0.228 |
| (no innovation) | none | 0% | 0.00 ± 0.00 | 0.0 | 0.228 |

Adoption in each group (mean of the last 100 steps), seeded during scarcity:

| seeding | Dominant | Marginal | Open | Closed | shortage | sustained |
| --- | --- | --- | --- | --- | --- | --- |
| no innovation | 0.00 | 0.00 | 0.00 | 0.00 | 0.35 | 0% |
| every group | 1.00 | 0.28 | 0.99 | 1.00 | 0.04 | 0% |
| Dominant originate | 1.00 | 0.97 | 0.99 | 0.01 | 0.08 | 0% |
| Dominant introduce | 1.00 | 0.80 | 0.99 | 0.24 | 0.07 | 0% |
| Marginal originate | 0.00 | 0.00 | 0.00 | 0.00 | 0.35 | 0% |
| Marginal introduce | 0.00 | 0.01 | 0.00 | 0.00 | 0.35 | 0% |
| Open originate | 0.99 | 0.56 | 0.99 | 0.60 | 0.05 | 0% |
| Open introduce | 1.00 | 0.58 | 0.99 | 0.56 | 0.05 | 0% |
| Closed originate | 0.99 | 0.28 | 0.99 | 1.00 | 0.04 | 0% |
| Closed introduce | 0.99 | 0.28 | 0.99 | 1.00 | 0.04 | 0% |

The commons needs an overall adoption share of 0.87 (A*); "sustained" also needs the shortage to stay below the collapse threshold.


## (c) The threshold: extreme groups, no conformity, ρ = 0.75 (A* = 0.625)

`miras commons scenario examples/extremes.json --off tight_conformity --set resource.rho=0.75`

### Seeded during plenty

| seed group | mode | sustained | mean adoption | reach | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| Closed | introduce | 70% | 0.58 ± 0.08 | 2.3 | 0.055 |
| Closed | originate | 8% | 0.06 ± 0.06 | 0.2 | 0.172 |
| (every group) | all | 0% | 0.56 ± 0.00 | 2.0 | 0.034 |
| Open | introduce | 0% | 0.56 ± 0.00 | 2.0 | 0.035 |
| Dominant | introduce | 0% | 0.55 ± 0.02 | 2.0 | 0.038 |
| Open | originate | 0% | 0.54 ± 0.03 | 1.9 | 0.041 |
| Dominant | originate | 0% | 0.26 ± 0.08 | 0.9 | 0.116 |
| Marginal | introduce | 0% | 0.08 ± 0.01 | 0.1 | 0.188 |
| Marginal | originate | 0% | 0.00 ± 0.00 | 0.0 | 0.185 |
| (no innovation) | none | 0% | 0.00 ± 0.00 | 0.0 | 0.185 |

Adoption in each group (mean of the last 100 steps), seeded during plenty:

| seeding | Dominant | Marginal | Open | Closed | shortage | sustained |
| --- | --- | --- | --- | --- | --- | --- |
| no innovation | 0.00 | 0.00 | 0.00 | 0.00 | 0.25 | 0% |
| every group | 1.00 | 0.24 | 0.99 | 0.01 | 0.03 | 0% |
| Dominant originate | 0.46 | 0.11 | 0.46 | 0.00 | 0.15 | 0% |
| Dominant introduce | 0.97 | 0.24 | 0.97 | 0.01 | 0.04 | 0% |
| Marginal originate | 0.00 | 0.02 | 0.00 | 0.00 | 0.25 | 0% |
| Marginal introduce | 0.00 | 0.32 | 0.00 | 0.00 | 0.23 | 0% |
| Open originate | 0.95 | 0.23 | 0.95 | 0.01 | 0.04 | 0% |
| Open introduce | 0.99 | 0.25 | 0.99 | 0.01 | 0.03 | 0% |
| Closed originate | 0.08 | 0.00 | 0.08 | 0.08 | 0.23 | 8% |
| Closed introduce | 0.80 | 0.07 | 0.77 | 0.70 | 0.05 | 70% |

The commons needs an overall adoption share of 0.62 (A*); "sustained" also needs the shortage to stay below the collapse threshold.

### Seeded during scarcity

| seed group | mode | sustained | mean adoption | reach | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| Closed | originate | 14% | 0.58 ± 0.01 | 2.0 | 0.020 |
| Closed | introduce | 14% | 0.58 ± 0.01 | 2.0 | 0.021 |
| Open | originate | 0% | 0.56 ± 0.00 | 2.0 | 0.035 |
| Dominant | originate | 0% | 0.56 ± 0.00 | 2.0 | 0.035 |
| (every group) | all | 0% | 0.56 ± 0.00 | 2.0 | 0.034 |
| Dominant | introduce | 0% | 0.56 ± 0.00 | 2.0 | 0.035 |
| Open | introduce | 0% | 0.56 ± 0.00 | 2.0 | 0.035 |
| Marginal | introduce | 0% | 0.13 ± 0.01 | 0.6 | 0.190 |
| Marginal | originate | 0% | 0.01 ± 0.00 | 0.0 | 0.186 |
| (no innovation) | none | 0% | 0.00 ± 0.00 | 0.0 | 0.185 |

Adoption in each group (mean of the last 100 steps), seeded during scarcity:

| seeding | Dominant | Marginal | Open | Closed | shortage | sustained |
| --- | --- | --- | --- | --- | --- | --- |
| no innovation | 0.00 | 0.00 | 0.00 | 0.00 | 0.25 | 0% |
| every group | 1.00 | 0.24 | 0.99 | 0.01 | 0.03 | 0% |
| Dominant originate | 1.00 | 0.24 | 0.99 | 0.01 | 0.03 | 0% |
| Dominant introduce | 1.00 | 0.24 | 0.99 | 0.01 | 0.03 | 0% |
| Marginal originate | 0.00 | 0.05 | 0.00 | 0.00 | 0.25 | 0% |
| Marginal introduce | 0.00 | 0.54 | 0.00 | 0.00 | 0.21 | 0% |
| Open originate | 0.99 | 0.25 | 0.99 | 0.01 | 0.03 | 0% |
| Open introduce | 1.00 | 0.24 | 0.99 | 0.01 | 0.03 | 0% |
| Closed originate | 0.99 | 0.02 | 0.32 | 1.00 | 0.00 | 14% |
| Closed introduce | 0.99 | 0.02 | 0.31 | 0.99 | 0.00 | 14% |

The commons needs an overall adoption share of 0.62 (A*); "sustained" also needs the shortage to stay below the collapse threshold.


## (c) The threshold: extreme groups, no conformity, 1,500 steps

`miras commons scenario examples/extremes.json --off tight_conformity --steps 1500`

### Seeded during plenty

| seed group | mode | sustained | mean adoption | reach | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| Closed | introduce | 86% | 0.65 ± 0.07 | 2.6 | 0.046 |
| Closed | originate | 22% | 0.17 ± 0.09 | 0.7 | 0.164 |
| (every group) | all | 4% | 0.74 ± 0.00 | 3.0 | 0.044 |
| Dominant | introduce | 2% | 0.74 ± 0.00 | 3.0 | 0.046 |
| Open | originate | 0% | 0.74 ± 0.00 | 3.0 | 0.046 |
| Open | introduce | 0% | 0.74 ± 0.00 | 3.0 | 0.046 |
| Dominant | originate | 0% | 0.50 ± 0.10 | 2.0 | 0.097 |
| Marginal | introduce | 0% | 0.00 ± 0.00 | 0.0 | 0.205 |
| Marginal | originate | 0% | 0.00 ± 0.00 | 0.0 | 0.205 |
| (no innovation) | none | 0% | 0.00 ± 0.00 | 0.0 | 0.205 |

Adoption in each group (mean of the last 100 steps), seeded during plenty:

| seeding | Dominant | Marginal | Open | Closed | shortage | sustained |
| --- | --- | --- | --- | --- | --- | --- |
| no innovation | 0.00 | 0.00 | 0.00 | 0.00 | 0.30 | 0% |
| every group | 1.00 | 0.93 | 0.99 | 0.05 | 0.00 | 4% |
| Dominant originate | 0.68 | 0.66 | 0.67 | 0.00 | 0.10 | 0% |
| Dominant introduce | 1.00 | 0.95 | 0.99 | 0.03 | 0.01 | 2% |
| Marginal originate | 0.00 | 0.01 | 0.00 | 0.00 | 0.30 | 0% |
| Marginal introduce | 0.00 | 0.01 | 0.00 | 0.00 | 0.30 | 0% |
| Open originate | 0.99 | 0.97 | 0.99 | 0.01 | 0.01 | 0% |
| Open introduce | 0.99 | 0.97 | 0.99 | 0.01 | 0.01 | 0% |
| Closed originate | 0.22 | 0.02 | 0.21 | 0.22 | 0.23 | 22% |
| Closed introduce | 0.86 | 0.06 | 0.84 | 0.86 | 0.04 | 86% |

The commons needs an overall adoption share of 0.75 (A*); "sustained" also needs the shortage to stay below the collapse threshold.

### Seeded during scarcity

| seed group | mode | sustained | mean adoption | reach | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| Closed | introduce | 100% | 0.76 ± 0.00 | 3.0 | 0.020 |
| Closed | originate | 100% | 0.76 ± 0.00 | 3.0 | 0.020 |
| (every group) | all | 92% | 0.76 ± 0.00 | 3.0 | 0.020 |
| Open | introduce | 8% | 0.74 ± 0.00 | 3.0 | 0.044 |
| Dominant | introduce | 6% | 0.74 ± 0.00 | 3.0 | 0.045 |
| Open | originate | 2% | 0.74 ± 0.00 | 3.0 | 0.046 |
| Dominant | originate | 0% | 0.74 ± 0.00 | 3.0 | 0.046 |
| Marginal | introduce | 0% | 0.00 ± 0.00 | 0.0 | 0.205 |
| Marginal | originate | 0% | 0.00 ± 0.00 | 0.0 | 0.205 |
| (no innovation) | none | 0% | 0.00 ± 0.00 | 0.0 | 0.205 |

Adoption in each group (mean of the last 100 steps), seeded during scarcity:

| seeding | Dominant | Marginal | Open | Closed | shortage | sustained |
| --- | --- | --- | --- | --- | --- | --- |
| no innovation | 0.00 | 0.00 | 0.00 | 0.00 | 0.30 | 0% |
| every group | 1.00 | 0.07 | 0.96 | 1.00 | 0.00 | 92% |
| Dominant originate | 1.00 | 0.97 | 0.99 | 0.01 | 0.00 | 0% |
| Dominant introduce | 0.99 | 0.92 | 0.99 | 0.07 | 0.00 | 6% |
| Marginal originate | 0.00 | 0.01 | 0.00 | 0.00 | 0.30 | 0% |
| Marginal introduce | 0.00 | 0.01 | 0.00 | 0.00 | 0.30 | 0% |
| Open originate | 0.99 | 0.95 | 0.99 | 0.03 | 0.01 | 2% |
| Open introduce | 0.99 | 0.90 | 0.99 | 0.09 | 0.00 | 8% |
| Closed originate | 0.99 | 0.07 | 0.97 | 1.00 | 0.00 | 100% |
| Closed introduce | 1.00 | 0.07 | 0.98 | 0.99 | 0.00 | 100% |

The commons needs an overall adoption share of 0.75 (A*); "sustained" also needs the shortage to stay below the collapse threshold.


