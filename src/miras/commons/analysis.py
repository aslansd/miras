"""Analysis of experiment summaries (the `*_summary.csv` files).

    miras commons analyze commons_output/e1_summary.csv
    miras commons analyze commons_output/e1_summary.csv commons_output/e1-off-power_share_summary.csv

With one file: references, main effects of each seed attribute, the power and
tightness dissections, the mode and timing contrasts, and the best seed groups.
With several: the same for the first, plus a side-by-side comparison of effect
sizes across runs (backgrounds for E1b, knockouts for E3), which is how a
result is traced to its mechanism.

Everything is computed from the per-cell means in the summaries, so each
number is an average over cells of 50-run means. Needs only numpy.
"""
from __future__ import annotations

import csv
import os

import numpy as np

ATTRS = ("tightness", "altruism", "parochialism", "wealth", "power")
LEVEL_NAMES = ("low", "mid", "high")
SINGLE = ("originate", "introduce")
DEFAULT_SAVING = 0.4


def read_summary(path):
    """Rows of a summary CSV with numbers converted. Summaries from 0.2.0 lack
    a_star and adoption_gap; they are filled in from rho (default saving)."""
    rows = []
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            row = {}
            for k, v in r.items():
                try:
                    row[k] = float(v)
                except (TypeError, ValueError):
                    row[k] = v
            if "a_star" not in row:
                row["a_star"] = (1 - row["rho"]) / DEFAULT_SAVING
                row["adoption_gap"] = row["mean_adoption_last"] - row["a_star"]
            rows.append(row)
    if not rows:
        raise ValueError(f"{path} has no rows")
    return rows


def run_name(path):
    return os.path.basename(path).replace("_summary.csv", "")


def _mean(rows, key):
    vals = [r[key] for r in rows if isinstance(r.get(key), float) and np.isfinite(r[key])]
    return float(np.mean(vals)) if vals else float("nan")


def _where(rows, **kw):
    out = rows
    for k, v in kw.items():
        if isinstance(v, (tuple, list, set)):
            out = [r for r in out if r.get(k) in v]
        else:
            out = [r for r in out if r.get(k) == v]
    return out


def _levels(rows, attr):
    return sorted({r[f"seed_{attr}"] for r in rows if f"seed_{attr}" in r})


def _pct(x):
    return "–" if not np.isfinite(x) else f"{100 * x:.0f}%"


def _num(x, fmt="{:.2f}"):
    return "–" if not np.isfinite(x) else fmt.format(x)


def _signed(x):
    return "–" if not np.isfinite(x) else f"{x:+.2f}"


def effect(rows, attr, outcome):
    """high-level mean minus low-level mean of `outcome` for seed attribute `attr`."""
    lv = _levels(rows, attr)
    if len(lv) < 2:
        return float("nan")
    return _mean(_where(rows, **{f"seed_{attr}": lv[-1]}), outcome) - \
        _mean(_where(rows, **{f"seed_{attr}": lv[0]}), outcome)


# --------------------------------------------------------------------------- #
def overview(runs, rhos):
    out = ["## Overview", "",
           "Share of runs that sustain the commons, by seeding mode (single-seed modes averaged "
           "over all seed profiles), and the mean adoption gap of single seeds (adoption minus "
           "the share A* the commons needs; negative = short of it).", ""]
    out.append("| run | rho | no innovation | every group | originate | introduce | "
               "best single profile | adoption gap (single seeds) |")
    out.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for name, rows in runs.items():
        for rho in rhos:
            s = _where(rows, rho=rho)
            if not s:
                continue
            single = _where(s, mode=SINGLE)
            best = max((r["sustained"] for r in single), default=float("nan"))
            out.append(f"| {name} | {rho:g} | {_pct(_mean(_where(s, mode='none'), 'sustained'))} | "
                       f"{_pct(_mean(_where(s, mode='all'), 'sustained'))} | "
                       f"{_pct(_mean(_where(s, mode='originate'), 'sustained'))} | "
                       f"{_pct(_mean(_where(s, mode='introduce'), 'sustained'))} | "
                       f"{_pct(best)} | {_signed(_mean(single, 'adoption_gap'))} |")
    return out + [""]


def main_effects(rows, rho, name):
    s = _where(rows, rho=rho)
    out = [f"### Main effects of the seed group's attributes ({name}, rho = {rho:g})", "",
           "Mean over the other attributes and over the conditions in the file. "
           "Sustained share / mean adoption.", "",
           "| attribute | mode | low | mid | high | high - low (sustained) |",
           "| --- | --- | --- | --- | --- | --- |"]
    for a in ATTRS:
        lv = _levels(s, a)
        for mode in SINGLE:
            m = _where(s, mode=mode)
            cells = [f"{_pct(_mean(_where(m, **{f'seed_{a}': v}), 'sustained'))} / "
                     f"{_num(_mean(_where(m, **{f'seed_{a}': v}), 'mean_adoption_last'))}" for v in lv]
            out.append(f"| {a} | {mode} | " + " | ".join(cells) + f" | {_signed(effect(m, a, 'sustained'))} |")
    return out + [""]


def power_dissection(rows, rho, name):
    s = _where(rows, rho=rho, mode="originate")
    out = [f"### Where adoption happens, by the seed group's power ({name}, rho = {rho:g}, originate)", "",
           "| seed power | seed-group adoption | other groups' adoption | groups reached | sustained | Gini of payoffs |",
           "| --- | --- | --- | --- | --- | --- |"]
    for v in _levels(s, "power"):
        m = _where(s, seed_power=v)
        out.append(f"| {v:g} | {_num(_mean(m, 'seed_group_adoption'))} | "
                   f"{_num(_mean(m, 'other_groups_adoption'))} | {_num(_mean(m, 'reach'), '{:.1f}')} | "
                   f"{_pct(_mean(m, 'sustained'))} | {_num(_mean(m, 'gini_payoff'), '{:.3f}')} |")
    return out + [""]


def tightness_by_power(rows, rho, name):
    s = _where(rows, rho=rho, mode="originate")
    pw = _levels(s, "power")
    out = [f"### Sustained share by seed tightness and power ({name}, rho = {rho:g}, originate)", "",
           "| tightness / power | " + " | ".join(f"{p:g}" for p in pw) + " |",
           "| --- | " + " | ".join("---" for _ in pw) + " |"]
    for t in _levels(s, "tightness"):
        out.append(f"| {t:g} | " + " | ".join(
            _pct(_mean(_where(s, seed_tightness=t, seed_power=p), "sustained")) for p in pw) + " |")
    return out + [""]


def mode_contrast(rows, rho, name):
    s = _where(rows, rho=rho)
    out = [f"### Introduce minus originate, by the seed group's parochialism ({name}, rho = {rho:g})", "",
           "| parochialism | sustained | mean adoption |", "| --- | --- | --- |"]
    for v in _levels(s, "parochialism"):
        i = _where(s, mode="introduce", seed_parochialism=v)
        o = _where(s, mode="originate", seed_parochialism=v)
        out.append(f"| {v:g} | {_signed(_mean(i, 'sustained') - _mean(o, 'sustained'))} | "
                   f"{_signed(_mean(i, 'mean_adoption_last') - _mean(o, 'mean_adoption_last'))} |")
    return out + [""]


def timing_contrast(rows, rho, name):
    s = _where(rows, rho=rho)
    if len({r.get("timing") for r in s}) < 2:
        return []
    out = [f"### Seeding at scarcity minus during plenty ({name}, rho = {rho:g})", "",
           "| mode | sustained | mean adoption |", "| --- | --- | --- |"]
    for mode in ("all",) + SINGLE:
        a = _where(s, mode=mode, timing="scarcity")
        b = _where(s, mode=mode, timing="plenty")
        out.append(f"| {mode} | {_signed(_mean(a, 'sustained') - _mean(b, 'sustained'))} | "
                   f"{_signed(_mean(a, 'mean_adoption_last') - _mean(b, 'mean_adoption_last'))} |")
    return out + [""]


def best_profiles(rows, rho, name, top=5):
    s = _where(rows, rho=rho, mode=SINGLE)
    groups = {}
    for r in s:
        key = tuple(r[f"seed_{a}"] for a in ATTRS) + (r["mode"],)
        groups.setdefault(key, []).append(r)
    ranked = sorted(groups.items(), key=lambda kv: (-_mean(kv[1], "sustained"),
                                                    -_mean(kv[1], "mean_adoption_last")))[:top]
    out = [f"### Best seed groups ({name}, rho = {rho:g}; mean over conditions)", "",
           "| " + " | ".join(ATTRS) + " | mode | sustained | mean adoption |",
           "| " + " | ".join("---" for _ in ATTRS) + " | --- | --- | --- |"]
    for key, rs in ranked:
        out.append("| " + " | ".join(f"{v:g}" for v in key[:-1]) + f" | {key[-1]} | "
                   f"{_pct(_mean(rs, 'sustained'))} | {_num(_mean(rs, 'mean_adoption_last'))} |")
    return out + [""]


def comparison(runs, rhos):
    names = list(runs)
    out = ["## Comparison across runs", "",
           "Effect of each seed attribute (high minus low) on the sustained share, per run. "
           "An effect that shrinks or vanishes when a mechanism is switched off (E3) is carried by "
           "that mechanism; one that survives a different background (E1b) does not depend on it.", ""]
    for rho in rhos:
        for mode in SINGLE:
            out += [f"### rho = {rho:g}, {mode}", "",
                    "| attribute | " + " | ".join(names) + " |",
                    "| --- | " + " | ".join("---" for _ in names) + " |"]
            for a in ATTRS:
                out.append(f"| {a} | " + " | ".join(
                    _signed(effect(_where(runs[n], rho=rho, mode=mode), a, "sustained")) for n in names) + " |")
            out.append("| *power, low / mid / high* | " + " | ".join(
                " / ".join(_pct(_mean(_where(runs[n], rho=rho, mode=mode, seed_power=v), "sustained"))
                           for v in _levels(_where(runs[n], rho=rho), "power")) for n in names) + " |")
            out.append("")
            # the same on mean adoption: informative even where nothing is sustained
            out += ["Effect (high minus low) on mean adoption:", "",
                    "| attribute | " + " | ".join(names) + " |",
                    "| --- | " + " | ".join("---" for _ in names) + " |"]
            for a in ATTRS:
                out.append(f"| {a} | " + " | ".join(
                    _signed(effect(_where(runs[n], rho=rho, mode=mode), a, "mean_adoption_last"))
                    for n in names) + " |")
            out.append("")
    return out


def analyze(paths, rho=None):
    """Markdown report for one or more summary CSVs."""
    runs = {run_name(p): read_summary(p) for p in paths}
    all_rhos = sorted({r["rho"] for rows in runs.values() for r in rows}, reverse=True)
    rhos = [x for x in all_rhos if rho is None or x in [float(v) for v in rho]]
    first = next(iter(runs))
    out = ["# miras.commons analysis", "",
           f"Runs: {', '.join(f'`{n}`' for n in runs)}. Numbers are averages over cells of "
           f"50-run means (see each summary's `reps`); they are conditional on the model's "
           f"calibration (specification amendment A3).", ""]
    out += overview(runs, rhos)
    out += [f"## Details for `{first}`", ""]
    for r in rhos:
        out += main_effects(runs[first], r, first)
        out += power_dissection(runs[first], r, first)
        out += tightness_by_power(runs[first], r, first)
        out += mode_contrast(runs[first], r, first)
        out += timing_contrast(runs[first], r, first)
        out += best_profiles(runs[first], r, first)
    if len(runs) > 1:
        out += comparison(runs, rhos)
    return "\n".join(out) + "\n"
