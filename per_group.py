"""Per-group adoption for a miras.commons scenario file (miras 0.2.1).

    python per_group.py extremes.json
    python per_group.py extremes.json --off power_share
    python per_group.py extremes.json --off tight_conformity --timing plenty

For each seeding (every group, then each group in each mode) it prints the
adoption share in each group over the last 100 steps, the mean shortage and
how many runs sustained the commons. The scenario command reports only the
seed group and "everyone else"; this shows which groups hold out.
"""
import argparse

import numpy as np
from miras.commons import experiments as ex

p = argparse.ArgumentParser()
p.add_argument("config")
p.add_argument("--off", default="", help="comma-separated mechanisms to switch off")
p.add_argument("--timing", default="scarcity", choices=("plenty", "scarcity"))
p.add_argument("--reps", type=int, default=10)
p.add_argument("--steps", type=int, default=500)
p.add_argument("--seed", type=int, default=1)
a = p.parse_args()

cfg = ex.load_config(a.config)
base = ex.base_settings(tuple(x for x in a.off.split(",") if x), a.steps)
names = [g["name"] for g in cfg["groups"]]
w = max(12, *(len(n) + 2 for n in names))
print(f"timing: {a.timing}" + (f"; off: {a.off}" if a.off else ""))
print(f"{'seeding':<24}" + "".join(f"{n:>{w}}" for n in names) + f"{'shortage':>10}{'sustained':>11}")
seedings = [("all", 0)] + [(m, i) for i in range(len(names)) for m in ("originate", "introduce")]
for mode, i in seedings:
    model, sd = ex.build_scenario({"mode": mode, "seed_index": i, "timing": a.timing}, cfg, base)
    ad, sh, ok = [], [], 0
    for r in range(a.reps):
        res = model.run(a.steps, sd, seed=a.seed + r)
        ad.append(res.adoption[-100:].mean(axis=0))
        sh.append(res.shortage[-100:].mean())
        ok += res.outcomes()["sustained"]
    label = "every group" if mode == "all" else f"{names[i]} {mode}"
    print(f"{label:<24}" + "".join(f"{x:>{w}.2f}" for x in np.mean(ad, axis=0))
          + f"{np.mean(sh):>10.2f}{ok:>7}/{a.reps}")
