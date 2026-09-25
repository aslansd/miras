"""Can a cross-sectional study recover conformity and migration?

The motivating example for miras. In the ABC analysis of Deffner et al. (2024)
cultural F_ST was the only summary statistic, and the posterior put most of its
mass on the wrong (theta, m) combination. This script asks the general question:
for which study designs are the conformity exponent and the migration rate
separately recoverable?

One reference table is simulated with every candidate summary; each design
is then evaluated by selecting its summaries, with no further simulation.

    python examples/equifinality.py --n-reference 2000 --cores 8
"""
import argparse
import os

import miras
from miras import (Conformity, CrossSectional, Islands, Model, ModelSimulator, ReferenceTable,
                   Uniform, WrightFisher, identify)

DESIGNS = {
    "F_ST only (as in the paper)": ["fst"],
    "F_ST + within-group diversity": ["fst", "within_diversity"],
    "F_ST + majority share + variants per group": ["fst", "majority_share", "n_variants"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-reference", type=int, default=2000)
    ap.add_argument("--n-test", type=int, default=150)
    ap.add_argument("--cores", type=int, default=os.cpu_count())
    ap.add_argument("--outdir", default="equifinality_output")
    ap.add_argument("--track", action="store_true", help="record with daftar")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    model = Model(structure=Islands(n_groups=20, group_size=50), demography=WrightFisher(),
                  learning=Conformity(), innovation=0.05, n_models=20)
    all_summaries = sorted({s for d in DESIGNS.values() for s in d})
    sim = ModelSimulator(model, summaries=all_summaries, n_steps=150,
                         design=CrossSectional(n_per_group=30))    # 30 respondents per village
    priors = {"learning.theta": Uniform(0.5, 3.0), "migration": Uniform(0.0, 0.4)}

    path = os.path.join(args.outdir, "reference_table.npz")
    if os.path.exists(path):
        table = ReferenceTable.load(path, priors)
    else:
        print(f"Simulating reference table ({args.n_reference} runs) ...", flush=True)
        table = ReferenceTable.build(sim, priors, args.n_reference, seed=1, cores=args.cores)
        table.save(path)

    for k, (label, summaries) in enumerate(DESIGNS.items()):
        report = identify(sim, priors, table=table.select(summaries), n_test=args.n_test,
                          track=args.track, label=f"equifinality-design-{k}")
        print(f"\n=== {label} ===")
        print(report.summary())
        report.plot(os.path.join(args.outdir, f"design_{k}.png"))
        with open(os.path.join(args.outdir, f"design_{k}.md"), "w") as fh:
            fh.write(f"# {label}\n\n" + report.to_markdown())


if __name__ == "__main__":
    main()
