"""Identifiability for miras.commons (0.2.3): which field data could tell the
model's mechanisms apart?

The October 2026 runs found two barriers to a water-saving practice:
conformity in tight groups (the conformity exponent theta, `learning.theta`)
and unequal water shares in a shortage (the power weighting of entitlements,
`learning.gamma_share`; 0 = equal shares). Which one binds depends on the
calibration (findings 4, 6 and 25), so a study that wants to know which one
holds the practice back in a real basin must be able to estimate both.

`CommonsSimulator` turns a scenario into the data a field study would
collect, for several study designs at once; `identify_designs` builds one
reference table and asks `miras.identify` what each design can recover.

Designs (columns of the simulated data):

- ``survey``: one survey at the end: the share of adopters in each group,
  from `n_respondents` people per group.
- ``survey+water``: the survey plus each group's water shortfall over the
  last 50 steps (water-delivery records).
- ``panel``: the survey repeated at `waves` evenly spaced times.
- ``panel+water``: the panel plus each group's shortfall before each wave.
"""
from __future__ import annotations

import json

import numpy as np

from ..inference.abc import ReferenceTable
from ..inference.priors import LogUniform, Priors, Uniform
from .experiments import (apply_sets, base_settings, build_scenario, check_config,
                          example_scenario_json, group_names)

# parameters a study might want to recover: name -> (Learning field, prior)
PARAMETERS = {
    "theta": ("theta", Uniform(1.0, 3.0)),                 # conformity exponent
    "gamma_share": ("gamma_share", Uniform(0.0, 2.0)),     # power weighting of water shares
    "lambda0": ("lambda0", LogUniform(1.0, 16.0)),         # value of saved water, empty store
    "beta_s": ("beta_s", LogUniform(2.5, 40.0)),           # payoff-learning slope
}
DEFAULT_PARAMETERS = ("theta", "gamma_share", "lambda0")

DESIGNS = {
    "survey": "one survey at the end: adoption in each group",
    "survey+water": "the survey plus each group's water shortfall (records)",
    "panel": "the survey repeated at several waves",
    "panel+water": "the panel plus each group's water shortfall before each wave",
}

DEFAULT_SEEDING = {"mode": "introduce", "seed_index": 0, "timing": "scarcity"}
WATER_WINDOW = 50


def default_config():
    """The example scenario of `miras commons example`."""
    return check_config(json.loads(example_scenario_json()))


class CommonsSimulator:
    """A `miras.identify` simulator: parameters -> the data of a field study.

    `config` is a scenario (as for `miras commons scenario`); `seeding` says
    where and when the practice starts: a dict with `mode` (originate,
    introduce or all), `seed_index` (the seed group, by position) and
    `timing` (plenty or scarcity). Each call runs the model once and returns
    the columns of every design; `design_columns` says which belong to which.
    """

    def __init__(self, config=None, seeding=None, parameters=DEFAULT_PARAMETERS, n_steps=500,
                 n_respondents=100, waves=5, off=(), sets=None):
        self.config = check_config(apply_sets(config or default_config(), sets or {}))
        self.seeding = dict(DEFAULT_SEEDING, **(seeding or {}))
        unknown = [p for p in parameters if p not in PARAMETERS]
        if unknown:
            raise ValueError(f"unknown parameter(s) {', '.join(unknown)}; "
                             f"choose from {', '.join(PARAMETERS)}")
        self.parameters = tuple(parameters)
        self.n_steps = int(n_steps)
        self.n_respondents = int(n_respondents)
        self.waves = int(waves)
        if self.waves < 2:
            raise ValueError("a panel needs at least 2 waves")
        if self.n_steps < self.waves * WATER_WINDOW:
            raise ValueError(f"n_steps must be at least waves x {WATER_WINDOW}")
        self.off = tuple(off)
        self.groups = group_names(self.config)
        self.times = [int(round(self.n_steps * (k + 1) / self.waves)) for k in range(self.waves)]
        cols = []
        for k in range(self.waves):
            cols += [f"adoption_w{k + 1}_{g}" for g in self.groups]
            cols += [f"shortfall_w{k + 1}_{g}" for g in self.groups]
        self.summary_names = tuple(cols)

    def priors(self):
        return Priors({p: PARAMETERS[p][1] for p in self.parameters})

    def design_columns(self, design):
        last = self.waves
        if design == "survey":
            ks, water = [last], False
        elif design == "survey+water":
            ks, water = [last], True
        elif design == "panel":
            ks, water = range(1, last + 1), False
        elif design == "panel+water":
            ks, water = range(1, last + 1), True
        else:
            raise ValueError(f"unknown design '{design}'; choose from {', '.join(DESIGNS)}")
        out = []
        for k in ks:
            out += [f"adoption_w{k}_{g}" for g in self.groups]
            if water:
                out += [f"shortfall_w{k}_{g}" for g in self.groups]
        return out

    def __call__(self, params, seed):
        rng = np.random.default_rng(seed)
        cfg = apply_sets(self.config, {"learning": {PARAMETERS[p][0]: float(v)
                                                    for p, v in params.items()}})
        model, sd = build_scenario(self.seeding, cfg, base_settings(self.off, self.n_steps))
        res = model.run(self.n_steps, sd, rng=rng)
        n = np.array([min(self.n_respondents, s) for s in res.sizes])
        row = []
        for t in self.times:
            true = res.adoption[t - 1]
            row += list(rng.binomial(n, true) / n)                # survey answers
            row += list(res.shortfall[t - WATER_WINDOW:t].mean(axis=0))
        return np.array(row, float)

    def describe(self):
        return {"simulator": "miras.commons.identify.CommonsSimulator",
                "groups": self.groups, "seeding": self.seeding, "parameters": list(self.parameters),
                "n_steps": self.n_steps, "n_respondents": self.n_respondents,
                "waves": self.times, "off": list(self.off)}


def identify_designs(simulator, designs=tuple(DESIGNS), *, n_reference=2000, n_test=50,
                     accept=0.05, seed=0, cores=1, table=None, track=False):
    """One reference table, every design: returns ({design: report}, table).

    The designs differ only in which columns they observe, so the same
    simulations serve all of them (ReferenceTable.select)."""
    from ..identify import identify
    pr = simulator.priors()
    if table is None:
        table = ReferenceTable.build(simulator, pr, n_reference, seed=seed, cores=cores)
    reports = {}
    for d in designs:
        sub = table.select(simulator.design_columns(d))
        rep = identify(simulator, pr, table=sub, n_test=n_test, accept=accept, seed=seed,
                       track=track, label=f"miras-commons-identify-{d}")
        rep.info["design"] = d
        reports[d] = rep
    return reports, table


def designs_report(reports, simulator):
    """Markdown comparison of the designs, then each design's findings."""
    names = list(simulator.parameters)
    sd = simulator.describe()
    out = ["# miras.commons identifiability", "",
           f"Groups: {', '.join(sd['groups'])}. Seeding: {sd['seeding']['mode']} "
           f"(group {sd['groups'][sd['seeding']['seed_index']]}) during {sd['seeding']['timing']}. "
           f"{sd['n_steps']} steps; surveys of {sd['n_respondents']} people per group at steps "
           f"{', '.join(map(str, sd['waves']))}"
           + (f"; mechanisms off: {', '.join(sd['off'])}" if sd["off"] else "") + ".", "",
           "Contraction: how much the data narrow the prior (0 = not at all, 1 = fully), "
           "averaged over test datasets. Coverage: how often the 90% interval contains the "
           "truth (should be near 0.90).", "",
           "| design | " + " | ".join(f"{n} contraction" for n in names) + " | findings |",
           "| --- | " + " | ".join("---" for _ in names) + " | --- |"]
    for d, rep in reports.items():
        c = {p["name"]: p["contraction"] for p in rep.parameters}
        f = "; ".join(f"{x.id} ({', '.join(x.params)})" for x in rep.findings) or "none"
        out.append(f"| {d} | " + " | ".join(f"{c[n]:.2f}" for n in names) + f" | {f} |")
    out += ["", "| design | " + " | ".join(f"{n} coverage" for n in names) + " |",
            "| --- | " + " | ".join("---" for _ in names) + " |"]
    for d, rep in reports.items():
        c = {p["name"]: p["coverage90"] for p in rep.parameters}
        out.append(f"| {d} | " + " | ".join(f"{c[n]:.2f}" for n in names) + " |")
    out.append("")
    for d, rep in reports.items():
        out += [f"## {d}: {DESIGNS[d]}", "", f"{len(simulator.design_columns(d))} observed numbers.", ""]
        if not rep.findings:
            out.append("No findings.")
        for f in rep.findings:
            where = f" *where {f.where}*" if f.where else ""
            out.append(f"- **{f.id}** ({f.severity}) `{'`, `'.join(f.params)}`{where}: {f.what}")
        out.append("")
    return "\n".join(out) + "\n"
