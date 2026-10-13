# miras.commons analysis

Runs: `e1`, `e1-rho0.7`. Numbers are averages over cells of 50-run means (see each summary's `reps`); they are conditional on the model's calibration (specification amendment A3).

## Overview

Share of runs that sustain the commons, by seeding mode (single-seed modes averaged over all seed profiles), and the mean adoption gap of single seeds (adoption minus the share A* the commons needs; negative = short of it).

| run | rho | no innovation | every group | originate | introduce | best single profile | adoption gap (single seeds) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| e1 | 0.7 | 0% | 96% | 25% | 25% | 100% | -0.43 |
| e1-rho0.7 | 0.7 | 0% | 96% | 25% | 25% | 100% | -0.43 |

## Details for `e1`

### Main effects of the seed group's attributes (e1, rho = 0.7)

Mean over the other attributes and over the conditions in the file. Sustained share / mean adoption.

| attribute | mode | low | mid | high | high - low (sustained) |
| --- | --- | --- | --- | --- | --- |
| tightness | originate | 45% / 0.50 | 30% / 0.35 | 1% / 0.05 | -0.44 |
| tightness | introduce | 47% / 0.55 | 26% / 0.37 | 1% / 0.07 | -0.46 |
| altruism | originate | 12% / 0.18 | 28% / 0.33 | 35% / 0.40 | +0.23 |
| altruism | introduce | 13% / 0.23 | 28% / 0.36 | 32% / 0.41 | +0.19 |
| parochialism | originate | 25% / 0.30 | 25% / 0.30 | 25% / 0.31 | +0.00 |
| parochialism | introduce | 31% / 0.38 | 26% / 0.34 | 17% / 0.27 | -0.14 |
| wealth | originate | 20% / 0.24 | 26% / 0.31 | 30% / 0.36 | +0.10 |
| wealth | introduce | 21% / 0.30 | 26% / 0.33 | 27% / 0.36 | +0.06 |
| power | originate | 0% / 0.08 | 46% / 0.47 | 29% / 0.36 | +0.29 |
| power | introduce | 0% / 0.09 | 46% / 0.53 | 28% / 0.38 | +0.28 |

### Where adoption happens, by the seed group's power (e1, rho = 0.7, originate)

| seed power | seed-group adoption | other groups' adoption | groups reached | sustained | Gini of payoffs |
| --- | --- | --- | --- | --- | --- |
| 0.5 | 0.40 | 0.00 | 0.4 | 0% | 0.074 |
| 1 | 0.39 | 0.50 | 2.4 | 46% | 0.009 |
| 2 | 0.31 | 0.39 | 1.8 | 29% | 0.059 |

### Sustained share by seed tightness and power (e1, rho = 0.7, originate)

| tightness / power | 0.5 | 1 | 2 |
| --- | --- | --- | --- |
| 0.1 | 0% | 79% | 55% |
| 0.5 | 0% | 57% | 33% |
| 0.9 | 0% | 2% | 0% |

### Introduce minus originate, by the seed group's parochialism (e1, rho = 0.7)

| parochialism | sustained | mean adoption |
| --- | --- | --- |
| 0.1 | +0.06 | +0.08 |
| 0.5 | +0.01 | +0.04 |
| 0.9 | -0.08 | -0.04 |

### Seeding at scarcity minus during plenty (e1, rho = 0.7)

| mode | sustained | mean adoption |
| --- | --- | --- |
| all | +0.07 | +0.08 |
| originate | +0.09 | +0.13 |
| introduce | +0.04 | +0.07 |

### Best seed groups (e1, rho = 0.7; mean over conditions)

| tightness | altruism | parochialism | wealth | power | mode | sustained | mean adoption |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.1 | 0.9 | 0.1 | 2 | 1 | introduce | 96% | 0.89 |
| 0.1 | 0.9 | 0.1 | 1 | 1 | originate | 96% | 0.87 |
| 0.1 | 0.9 | 0.1 | 1 | 1 | introduce | 96% | 0.85 |
| 0.1 | 0.9 | 0.5 | 1 | 1 | originate | 95% | 0.85 |
| 0.1 | 0.5 | 0.1 | 1 | 1 | introduce | 95% | 0.84 |

## Comparison across runs

Effect of each seed attribute (high minus low) on the sustained share, per run. An effect that shrinks or vanishes when a mechanism is switched off (E3) is carried by that mechanism; one that survives a different background (E1b) does not depend on it.

### rho = 0.7, originate

| attribute | e1 | e1-rho0.7 |
| --- | --- | --- |
| tightness | -0.44 | -0.44 |
| altruism | +0.23 | +0.23 |
| parochialism | +0.00 | +0.00 |
| wealth | +0.10 | +0.09 |
| power | +0.29 | +0.29 |
| *power, low / mid / high* | 0% / 46% / 29% | 0% / 46% / 30% |

Effect (high minus low) on mean adoption:

| attribute | e1 | e1-rho0.7 |
| --- | --- | --- |
| tightness | -0.45 | -0.45 |
| altruism | +0.22 | +0.22 |
| parochialism | +0.01 | +0.01 |
| wealth | +0.12 | +0.12 |
| power | +0.28 | +0.28 |

### rho = 0.7, introduce

| attribute | e1 | e1-rho0.7 |
| --- | --- | --- |
| tightness | -0.46 | -0.46 |
| altruism | +0.19 | +0.19 |
| parochialism | -0.14 | -0.14 |
| wealth | +0.06 | +0.07 |
| power | +0.28 | +0.28 |
| *power, low / mid / high* | 0% / 46% / 28% | 0% / 46% / 28% |

Effect (high minus low) on mean adoption:

| attribute | e1 | e1-rho0.7 |
| --- | --- | --- |
| tightness | -0.48 | -0.48 |
| altruism | +0.18 | +0.18 |
| parochialism | -0.11 | -0.11 |
| wealth | +0.07 | +0.07 |
| power | +0.29 | +0.30 |

