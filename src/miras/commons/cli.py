"""Command line for miras.commons.

    miras commons pilot                    # regimes at a glance (a minute or two)
    miras commons e1 --cores 8             # the main experiment (E1)
    miras commons e1 --background low      # E1b: background groups low (or high)
    miras commons scenario groups.json     # E2: your own groups
    ... --off tight_sanctions,power_share  # E3: knockouts, on any of the above

Long runs checkpoint every two minutes and on Ctrl-C; rerun the same command
to resume (identical results), or add --fresh to start over.
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np

from . import experiments as ex


def _common(p):
    p.add_argument("--reps", type=int, default=50, help="runs per cell")
    p.add_argument("--steps", type=int, default=500, help="steps per run")
    p.add_argument("--cores", type=int, default=os.cpu_count())
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--outdir", default="commons_output")
    p.add_argument("--off", default="", help="comma-separated mechanisms to switch off (E3)")
    p.add_argument("--fresh", action="store_true", help="ignore a checkpoint and start over")
    p.add_argument("--track", action="store_true", help="record the run with daftar")


def _off(args):
    return tuple(x.strip() for x in args.off.split(",") if x.strip())


def _run(cells, args, label, config=None):
    from ..provenance import tracked
    os.makedirs(args.outdir, exist_ok=True)
    off = _off(args)
    base = ex.base_settings(off, args.steps)
    tag = label + (("-off-" + "-".join(off)) if off else "")
    ck = ex.checkpoint_for(os.path.join(args.outdir, f"{tag}_checkpoint.npz"),
                           {"label": tag, "reps": args.reps, "steps": args.steps, "seed": args.seed,
                            "n_cells": len(cells)})
    if args.fresh:
        ck.remove()
    print(f"{len(cells)} cells x {args.reps} runs = {len(cells) * args.reps} runs on {args.cores} cores"
          + (f"; mechanisms off: {', '.join(off)}" if off else ""), flush=True)
    params = {"label": tag, "reps": args.reps, "steps": args.steps, "off": ",".join(off),
              "n_cells": len(cells)}
    with tracked(f"commons-{tag}", params=params, seed=args.seed, enabled=args.track) as run:
        out = ex.run_cells(cells, args.reps, cores=args.cores, seed=args.seed, steps=args.steps,
                           base=base, config=config, checkpoint=ck)
        rows = ex.summarise(cells, out)
        runs_path = os.path.join(args.outdir, f"{tag}_runs.csv")
        sum_path = os.path.join(args.outdir, f"{tag}_summary.csv")
        ex.write_runs(runs_path, cells, out)
        ex.write_summary(sum_path, rows)
        report = ex.scenario_report(rows, config) if config else ex.e1_report(rows)
        rep_path = os.path.join(args.outdir, f"{tag}_report.md")
        with open(rep_path, "w") as fh:
            fh.write(report)
        for pth in (runs_path, sum_path, rep_path):
            run.add_output(pth)
    print(f"\nWritten: {runs_path}\n         {sum_path}\n         {rep_path}")
    return rows, report


def cmd_e1(argv):
    p = argparse.ArgumentParser(prog="miras commons e1", description="E1 (and E1b, E3).")
    _common(p)
    p.add_argument("--background", choices=ex.LEVEL_NAMES, default="mid",
                   help="level of the four background groups (E1b: low or high)")
    p.add_argument("--quick", action="store_true", help="a tiny smoke test (2 reps, 100 steps)")
    args = p.parse_args(argv)
    if args.quick:
        args.reps, args.steps = 2, 100
    cells = ex.e1_cells(background=args.background)
    label = "e1" if args.background == "mid" else f"e1b-{args.background}"
    _run(cells, args, label + ("-quick" if args.quick else ""))
    return 0


def cmd_scenario(argv):
    p = argparse.ArgumentParser(prog="miras commons scenario",
                                description="E2: seed each of your groups in each mode.")
    p.add_argument("config", help="JSON file with groups (and optionally resource, innovation, learning)")
    _common(p)
    args = p.parse_args(argv)
    config = ex.load_config(args.config)
    name = os.path.splitext(os.path.basename(args.config))[0]
    _, report = _run(ex.scenario_cells(config), args, f"scenario-{name}", config=config)
    print("\n" + report)
    return 0


def cmd_pilot(argv):
    p = argparse.ArgumentParser(prog="miras commons pilot",
                                description="Which regimes occur: references and a mid-level seed group.")
    p.add_argument("--reps", type=int, default=10)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--off", default="")
    args = p.parse_args(argv)
    base = ex.base_settings(_off(args))
    mid = {f"seed_{k}": v[1] for k, v in ex.LEVELS.items()}
    print(f"{'rho':>5} {'contact':>7} {'timing':>8} {'mode':>10} | sustained  adoption  shortage  reach")
    for rho in ex.CONDITIONS["rho"]:
        for contact in ex.CONDITIONS["contact"]:
            for timing in ex.CONDITIONS["timing"]:
                for mode in ("none", "all", "originate", "introduce"):
                    cell = dict(rho=rho, contact=contact, timing=timing, background="mid",
                                n_groups=5, size=200, mode=mode, **mid)
                    model, sd = ex.build(cell, base)
                    o = [model.run(500, sd, seed=args.seed + r).outcomes() for r in range(args.reps)]
                    m = lambda k: np.mean([x[k] for x in o])
                    print(f"{rho:>5} {contact:>7} {timing:>8} {mode:>10} | {m('sustained'):>9.0%} "
                          f"{m('mean_adoption_last'):>9.3f} {m('mean_shortage_last'):>9.3f} {m('reach'):>6.1f}",
                          flush=True)
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmds = {"pilot": cmd_pilot, "e1": cmd_e1, "scenario": cmd_scenario}
    if not argv or argv[0] not in cmds:
        print(__doc__)
        return 0 if not argv or argv[0] in ("-h", "--help") else 2
    return cmds[argv[0]](argv[1:])
