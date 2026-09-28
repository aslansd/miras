"""The experiments of the miras.commons specification.

E1  which seed group works best: the seed group's five attributes on a 3-level
    factorial, x 2 modes (originate, introduce) x 8 conditions (water stress x
    contact x timing), plus the two reference runs (no innovation; every group
    seeded) per condition.
E1b the same with the background groups set low or high instead of middle.
E2  a scenario: your own groups, seeding each one in each mode.
E3  knockouts: any of the above with mechanisms switched off.

Every run's outcomes go to a CSV (one row per run); a summary CSV has the mean
and a 95% interval per cell, and a Markdown report gives the best seeding
choices per condition and the main effects of each seed attribute.
"""
from __future__ import annotations

import csv
import itertools
import json
import math
import os
from dataclasses import asdict, replace

import numpy as np

from ..runner import Checkpoint, Progress, interrupted_message, make_pool
from .model import CommonsModel, Group, Innovation, Learning, Mechanisms, Resource, Seeding

LEVELS = {
    "tightness": (0.1, 0.5, 0.9),
    "altruism": (0.1, 0.5, 0.9),
    "parochialism": (0.1, 0.5, 0.9),
    "wealth": (0.5, 1.0, 2.0),
    "power": (0.5, 1.0, 2.0),
}
LEVEL_NAMES = ("low", "mid", "high")
CONDITIONS = {"rho": (0.85, 0.7), "contact": (0.1, 0.3), "timing": ("plenty", "scarcity")}
MODES = ("originate", "introduce")
OUTCOMES = ("final_adoption", "mean_adoption_last", "sustained", "collapsed",
            "mean_shortage_last", "reach", "time_to_a_star", "gini_payoff",
            "seed_group_adoption", "other_groups_adoption", "a_star", "adoption_gap")


class ScenarioError(ValueError):
    """A problem with a scenario file, explained for the user."""


# --------------------------------------------------------------------------- #
# Backgrounds (0.2.1: one attribute at a time)
# --------------------------------------------------------------------------- #
def parse_background(spec="mid"):
    """Background levels per attribute from 'low' / 'mid' / 'high' (all five
    attributes) or 'attribute=level[,attribute=level...]' (the named ones;
    the rest stay mid). Returns {attribute: level name}."""
    spec = (spec or "mid").strip()
    if spec in LEVEL_NAMES:
        return {k: spec for k in LEVELS}
    out = {k: "mid" for k in LEVELS}
    for part in spec.split(","):
        if "=" not in part:
            raise ValueError(f"background '{spec}': use low, mid, high or attribute=level "
                             f"(e.g. tightness=low,power=high)")
        k, v = (x.strip() for x in part.split("=", 1))
        if k not in LEVELS:
            raise ValueError(f"unknown attribute '{k}'; choose from {', '.join(LEVELS)}")
        if v not in LEVEL_NAMES:
            raise ValueError(f"unknown level '{v}'; choose from {', '.join(LEVEL_NAMES)}")
        out[k] = v
    return out


def background_label(levels):
    """'mid', 'low', 'high', or e.g. 'tightness-low' for mixed backgrounds."""
    vals = set(levels.values())
    if len(vals) == 1:
        return vals.pop()
    return "+".join(f"{k}-{v}" for k, v in levels.items() if v != "mid")


# --------------------------------------------------------------------------- #
# Cells
# --------------------------------------------------------------------------- #
def e1_cells(background="mid", n_groups=5, size=200, rho=None, contact=None, timing=None):
    """All E1 cells. A cell is a plain dict (so it can be written to CSV).

    background: see `parse_background` ('mid', 'low', 'high' or e.g.
    'tightness=low'). rho, contact, timing: optional lists restricting the
    conditions (e.g. rho=[0.7] for severe stress only)."""
    levels = parse_background(background)
    bg = {k: LEVELS[k][LEVEL_NAMES.index(v)] for k, v in levels.items()}
    rhos = CONDITIONS["rho"] if rho is None else tuple(float(x) for x in rho)
    contacts = CONDITIONS["contact"] if contact is None else tuple(float(x) for x in contact)
    timings = CONDITIONS["timing"] if timing is None else tuple(timing)
    for t in timings:
        if t not in ("plenty", "scarcity"):
            raise ValueError(f"timing must be plenty or scarcity, not '{t}'")
    cells = []
    for rho_, contact_, timing_ in itertools.product(rhos, contacts, timings):
        cond = {"rho": rho_, "contact": contact_, "timing": timing_,
                "background": background_label(levels), "n_groups": n_groups, "size": size,
                **{f"bg_{k}": v for k, v in bg.items()}}
        for mode in ("none", "all"):
            cells.append(dict(cond, mode=mode, **{f"seed_{k}": bg[k] for k in LEVELS}))
        for combo in itertools.product(*LEVELS.values()):
            for mode in MODES:
                cells.append(dict(cond, mode=mode, **{f"seed_{k}": v for k, v in zip(LEVELS, combo)}))
    return cells


def build(cell, base=None):
    """(CommonsModel, Seeding) for a cell. `base` holds shared settings:
    innovation, learning, mechanisms (dataclasses) and steps."""
    base = base or {}
    if all(f"bg_{k}" in cell for k in LEVELS):
        bg = {k: cell[f"bg_{k}"] for k in LEVELS}
    else:                                   # cells written by 0.2.0
        bg_level = LEVEL_NAMES.index(cell.get("background", "mid"))
        bg = {k: v[bg_level] for k, v in LEVELS.items()}
    seed_attrs = {k: cell[f"seed_{k}"] for k in LEVELS}
    groups = [Group(name="seed", size=cell["size"], contact=cell["contact"], **seed_attrs)]
    groups += [Group(name=f"background{i}", size=cell["size"], contact=cell["contact"], **bg)
               for i in range(1, cell["n_groups"])]
    model = CommonsModel(groups, innovation=base.get("innovation"),
                         resource=Resource(rho=cell["rho"]), learning=base.get("learning"),
                         mechanisms=base.get("mechanisms"))
    return model, Seeding(mode=cell["mode"], group=0, timing=cell["timing"])


def scenario_cells(config):
    """E2: seed each of your groups in each mode, at each timing, plus the two
    references. `config` = {"groups": [...], "resource": {...}, ...}."""
    groups = [Group(**g) for g in config["groups"]]
    timings = config.get("timings", list(CONDITIONS["timing"]))
    cells = []
    for timing in timings:
        for mode in ("none", "all"):
            cells.append({"mode": mode, "seed_index": 0, "seed_name": "-", "timing": timing})
        for i, g in enumerate(groups):
            for mode in MODES:
                cells.append({"mode": mode, "seed_index": i, "seed_name": g.name, "timing": timing})
    return cells


def build_scenario(cell, config, base=None):
    base = base or {}
    groups = [Group(**g) for g in config["groups"]]
    model = CommonsModel(groups,
                         innovation=Innovation(**config.get("innovation", {})),
                         resource=Resource(**config.get("resource", {})),
                         learning=Learning(**config.get("learning", {})),
                         mechanisms=base.get("mechanisms"))
    return model, Seeding(mode=cell["mode"], group=cell["seed_index"], timing=cell["timing"])


# --------------------------------------------------------------------------- #
# Running
# --------------------------------------------------------------------------- #
def _job(args):
    k, cell, seed, steps, base, config = args
    model, sd = build_scenario(cell, config, base) if config else build(cell, base)
    o = model.run(steps, sd, seed=seed).outcomes()
    return k, np.array([float(o[name]) for name in OUTCOMES])


def run_cells(cells, reps, *, cores=1, seed=1, steps=500, base=None, config=None,
              checkpoint=None):
    """Run every cell `reps` times. Returns an array (n_cells, reps, n_outcomes).
    Run k = cell k // reps, replicate k % reps; its seed is fixed by k, so an
    interrupted run resumed from `checkpoint` gives identical results."""
    n = len(cells) * reps
    seeds = np.random.SeedSequence(seed).generate_state(n, dtype=np.uint64) % (2**63)
    out = np.full((len(cells), reps, len(OUTCOMES)), np.nan)
    done = np.zeros(n, bool)
    state = checkpoint.load() if checkpoint else None
    if state is not None:
        out, done = state["out"], state["done"].astype(bool)
        print(f"  resuming: {int(done.sum())}/{n} runs already done", flush=True)
    jobs = [(k, cells[k // reps], int(seeds[k]), steps, base, config) for k in np.flatnonzero(~done)]
    progress = Progress(n, already=int(done.sum()), every=max(10, min(1000, n // 50)))
    try:
        if cores > 1:
            with make_pool(cores) as pool:
                for k, vals in pool.imap_unordered(_job, jobs, chunksize=8):
                    out[k // reps, k % reps], done[k] = vals, True
                    progress.tick()
                    if checkpoint and checkpoint.due():
                        checkpoint.save(out=out, done=done)
        else:
            for job in jobs:
                k, vals = _job(job)
                out[k // reps, k % reps], done[k] = vals, True
                progress.tick()
                if checkpoint and checkpoint.due():
                    checkpoint.save(out=out, done=done)
    except KeyboardInterrupt:
        if checkpoint:
            checkpoint.save(out=out, done=done)
            print(interrupted_message(int(done.sum()), n, checkpoint.path))
        raise
    if checkpoint:
        checkpoint.remove()
    return out


# --------------------------------------------------------------------------- #
# Output and analysis
# --------------------------------------------------------------------------- #
def write_runs(path, cells, out):
    keys = list(cells[0])
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(keys + ["replicate"] + list(OUTCOMES))
        for c, cell in enumerate(cells):
            for r in range(out.shape[1]):
                w.writerow([cell[k] for k in keys] + [r] + [f"{v:.6g}" for v in out[c, r]])


def summarise(cells, out):
    """Per cell: mean and 95% interval (normal approximation) of each outcome."""
    rows = []
    reps = out.shape[1]
    for c, cell in enumerate(cells):
        row = dict(cell)
        for j, name in enumerate(OUTCOMES):
            x = out[c, :, j]
            x = x[np.isfinite(x)]
            m = float(x.mean()) if x.size else float("nan")
            half = 1.96 * float(x.std(ddof=1)) / math.sqrt(x.size) if x.size > 1 else float("nan")
            row[name] = m
            row[f"{name}_ci"] = half
        row["reps"] = reps
        rows.append(row)
    return rows


def write_summary(path, rows):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def _fmt_profile(r):
    names = {k: LEVEL_NAMES[LEVELS[k].index(r[f"seed_{k}"])] for k in LEVELS if f"seed_{k}" in r}
    return ", ".join(f"{k} {v}" for k, v in names.items())


def e1_report(rows, top=3):
    """Markdown: per condition, the references, the best seed profiles and the
    main effects of each attribute on sustained adoption."""
    out = ["# E1 results", ""]
    conds = sorted({(r["rho"], r["contact"], r["timing"]) for r in rows})
    for rho, contact, timing in conds:
        sub = [r for r in rows if (r["rho"], r["contact"], r["timing"]) == (rho, contact, timing)]
        ref = {r["mode"]: r for r in sub if r["mode"] in ("none", "all")}
        out += [f"## Water stress rho = {rho}, contact = {contact}, seeded during {timing}", ""]
        out.append(f"References: no innovation sustained {ref['none']['sustained']:.0%}; "
                   f"every group seeded sustained {ref['all']['sustained']:.0%} "
                   f"(mean adoption {ref['all']['mean_adoption_last']:.2f}).")
        out.append("")
        for mode in MODES:
            ms = [r for r in sub if r["mode"] == mode]
            best = sorted(ms, key=lambda r: (-r["sustained"], -r["mean_adoption_last"]))[:top]
            out.append(f"**{mode}**, best seed groups:")
            out.append("")
            out.append("| seed group | sustained | mean adoption | reach |")
            out.append("| --- | --- | --- | --- |")
            for r in best:
                out.append(f"| {_fmt_profile(r)} | {r['sustained']:.0%} | "
                           f"{r['mean_adoption_last']:.2f} \u00b1 {r['mean_adoption_last_ci']:.2f} | "
                           f"{r['reach']:.1f} |")
            out.append("")
            out.append("Main effects on mean adoption (average over the other attributes):")
            out.append("")
            out.append("| attribute | low | mid | high |")
            out.append("| --- | --- | --- | --- |")
            for k, vals in LEVELS.items():
                cols = [np.mean([r["mean_adoption_last"] for r in ms if r[f"seed_{k}"] == v]) for v in vals]
                out.append(f"| {k} | " + " | ".join(f"{c:.3f}" for c in cols) + " |")
            out.append("")
    return "\n".join(out) + "\n"


def scenario_report(rows, config):
    out = ["# Scenario results", ""]
    for timing in sorted({r["timing"] for r in rows}):
        sub = [r for r in rows if r["timing"] == timing]
        out += [f"## Seeded during {timing}", "",
                "| seed group | mode | sustained | mean adoption | reach | Gini of payoffs |",
                "| --- | --- | --- | --- | --- | --- |"]
        for r in sorted(sub, key=lambda r: (-r["sustained"], -r["mean_adoption_last"])):
            name = {"none": "(no innovation)", "all": "(every group)"}.get(r["mode"], r["seed_name"])
            out.append(f"| {name} | {r['mode']} | {r['sustained']:.0%} | "
                       f"{r['mean_adoption_last']:.2f} \u00b1 {r['mean_adoption_last_ci']:.2f} | "
                       f"{r['reach']:.1f} | {r['gini_payoff']:.3f} |")
        out.append("")
    return "\n".join(out) + "\n"


def base_settings(off=(), steps=500):
    mech = Mechanisms().without(*off) if off else Mechanisms()
    return {"mechanisms": mech, "innovation": Innovation(), "learning": Learning(), "steps": steps}


EXAMPLE_SCENARIO = {
    "groups": [
        {"name": "Highland", "size": 300, "tightness": 0.8, "altruism": 0.6,
         "parochialism": 0.7, "wealth": 1.5, "power": 2.0, "contact": 0.1},
        {"name": "Valley", "size": 200, "tightness": 0.3, "altruism": 0.7,
         "parochialism": 0.3, "wealth": 1.0, "power": 1.0, "contact": 0.2},
        {"name": "Riverside", "size": 150, "tightness": 0.5, "altruism": 0.4,
         "parochialism": 0.5, "wealth": 0.6, "power": 0.5, "contact": 0.3},
    ],
    "resource": {"rho": 0.7},
    "innovation": {"saving": 0.4, "cost": 0.1},
    "timings": ["plenty", "scarcity"],
}


def example_scenario_json() -> str:
    return json.dumps(EXAMPLE_SCENARIO, indent=2) + "\n"


def load_config(path):
    """Read and check a scenario file; every problem is a ScenarioError with a
    message that says what to change."""
    import dataclasses
    hint = f"Create one with: miras commons example > {path}"
    if not os.path.exists(path):
        raise ScenarioError(f"scenario file '{path}' not found (in {os.getcwd()}). {hint}")
    try:
        with open(path) as fh:
            cfg = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ScenarioError(f"'{path}' is not valid JSON: {exc}") from None
    if not isinstance(cfg, dict) or not isinstance(cfg.get("groups"), list) or not cfg["groups"]:
        raise ScenarioError(f"'{path}' needs a non-empty \"groups\" list. {hint}")
    allowed = {"groups", "resource", "innovation", "learning", "timings"}
    extra = set(cfg) - allowed
    if extra:
        raise ScenarioError(f"unknown top-level key(s) {sorted(extra)}; allowed: {sorted(allowed)}")
    sections = {"groups": Group, "resource": Resource, "innovation": Innovation,
                "learning": Learning}
    for key, cls in sections.items():
        fields = {f.name for f in dataclasses.fields(cls)}
        items = cfg.get(key, [] if key == "groups" else {})
        for i, item in enumerate(items if key == "groups" else [items]):
            where = f"group {i + 1}" if key == "groups" else f'"{key}"'
            if not isinstance(item, dict):
                raise ScenarioError(f"{where} must be an object with named fields")
            bad = set(item) - fields
            if bad:
                raise ScenarioError(f"{where}: unknown field(s) {sorted(bad)}; "
                                    f"allowed: {', '.join(sorted(fields))}")
            try:
                cls(**item)
            except (TypeError, ValueError) as exc:
                raise ScenarioError(f"{where}: {exc}") from None
    names = [g.get("name", "group") for g in cfg["groups"]]
    if len(set(names)) != len(names):
        raise ScenarioError("group names must be unique (they label the results)")
    for t in cfg.get("timings", []):
        if t not in ("plenty", "scarcity"):
            raise ScenarioError(f'"timings" may contain plenty and scarcity, not {t!r}')
    return cfg


def checkpoint_for(path, key):
    from .. import __version__
    return Checkpoint(path, dict(key, version=__version__))


__all__ = ["LEVELS", "CONDITIONS", "MODES", "OUTCOMES", "ScenarioError", "parse_background",
           "background_label", "EXAMPLE_SCENARIO", "example_scenario_json", "e1_cells", "build", "scenario_cells",
           "build_scenario", "run_cells", "write_runs", "summarise", "write_summary",
           "e1_report", "scenario_report", "base_settings", "load_config", "checkpoint_for",
           "asdict", "replace"]
