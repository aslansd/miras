"""miras.commons 0.2.3: water shortfall per group, the low-shortage and
settled outcomes, and identifiability of the commons model across field
designs (`miras commons identify`)."""
import json

import numpy as np
import pytest

from miras.commons import experiments as ex
from miras.commons import identify as ci
from miras.commons.cli import main as commons_main
from miras.commons.model import (LOW_SHORTAGE, SETTLED_DRIFT, CommonsModel, Group, Learning,
                                 Resource, Seeding)

SMALL = {
    "groups": [{"name": "A", "size": 60, "tightness": 0.1, "power": 2.0},
               {"name": "B", "size": 40, "tightness": 0.9, "power": 0.5}],
    "resource": {"rho": 0.7},
    "timings": ["scarcity"],
}


def _model(gamma=1.0):
    return CommonsModel([Group("A", 60, power=2.0), Group("B", 40, power=0.5)],
                        resource=Resource(rho=0.7), learning=Learning(gamma_share=gamma))


# --- shortfall per group ------------------------------------------------------- #
def test_shortfall_adds_up_to_the_overall_shortage():
    """Group shortfalls weighted by each group's demand give the overall shortage."""
    model = _model()
    res = model.run(120, Seeding(mode="introduce", group=0, timing="scarcity"), seed=2)
    assert res.shortfall.shape == res.adoption.shape
    assert np.all((res.shortfall >= -1e-12) & (res.shortfall <= 1 + 1e-12))
    # demand in step t comes from the adoption recorded at the end of step t - 1
    demand = res.sizes * (1 - 0.4 * res.adoption[:-1])       # per-capita demand 1, saving 0.4
    overall = (res.shortfall[1:] * demand).sum(axis=1) / demand.sum(axis=1)
    np.testing.assert_allclose(overall, res.shortage[1:], atol=1e-9)


def test_power_weighted_shares_spare_the_powerful_group():
    res = _model(gamma=2.0).run(60, Seeding(mode="none", timing="scarcity"), seed=1)
    late = res.shortfall[-30:].mean(axis=0)
    assert late[0] < late[1]                                   # A (power 2) short less than B
    eq = _model(gamma=0.0).run(60, Seeding(mode="none", timing="scarcity"), seed=1)
    np.testing.assert_allclose(*eq.shortfall[-30:].mean(axis=0), atol=1e-9)   # equal shares


def test_new_outcomes_change_no_old_number():
    """Same seed, same numbers as 0.2.2 for every outcome 0.2.2 had."""
    cells = ex.scenario_cells(SMALL)
    out = ex.run_cells(cells, 2, seed=4, steps=150, base=ex.base_settings(), config=SMALL)
    old = len(ex.OUTCOMES) - 3
    assert ex.OUTCOMES[old:] == ("low_shortage", "adoption_drift", "settled")
    for k, cell in enumerate(cells):
        model, sd = ex.build_scenario(cell, SMALL, ex.base_settings())
        seeds = np.random.SeedSequence(4).generate_state(len(cells) * 2, dtype=np.uint64) % (2**63)
        o = model.run(150, sd, seed=int(seeds[2 * k])).outcomes()
        np.testing.assert_allclose(out[k, 0, :len(ex.OUTCOMES)], [float(o[n]) for n in ex.OUTCOMES])


def test_low_shortage_and_settled():
    model = _model()
    res = model.run(400, Seeding(mode="none", timing="scarcity"), seed=1)
    o = res.outcomes()
    assert o["adoption_drift"] == 0.0 and o["settled"]          # nothing to change
    assert not o["low_shortage"] and o["mean_shortage_last"] > LOW_SHORTAGE
    # a run whose adoption is still rising is not settled
    res.adoption[-100:] = np.linspace(0.3, 0.9, 100)[:, None]
    res.adoption[-200:-100] = 0.3
    o = res.outcomes()
    assert o["adoption_drift"] > SETTLED_DRIFT and not o["settled"]


def test_drift_for_short_runs_uses_halves():
    res = _model().run(60, Seeding(mode="introduce", group=0, timing="scarcity"), seed=3)
    o = res.outcomes()
    ov = res.overall
    assert o["adoption_drift"] == pytest.approx(ov[30:].mean() - ov[:30].mean())


def test_scenario_report_shows_endings():
    cells = ex.scenario_cells(SMALL)
    out = ex.run_cells(cells, 2, seed=1, steps=100, base=ex.base_settings(), config=SMALL)
    rows = ex.summarise(cells, out, ex.outcome_names(SMALL))
    report = ex.scenario_report(rows, SMALL)
    assert "| low shortage | settled |" in report and "*Settled*" in report


def test_analyze_reports_endings(tmp_path):
    from miras.commons import analysis
    cells = ex.e1_cells(rho=[0.7], contact=[0.1], timing=["scarcity"])[:12]
    out = ex.run_cells(cells, 2, seed=1, steps=60, base=ex.base_settings())
    p = tmp_path / "e1-x_summary.csv"
    ex.write_summary(p, ex.summarise(cells, out))
    report = analysis.analyze([str(p)])
    assert "## How runs end (0.2.3)" in report
    assert "| e1-x | 0.7 | every group |" in report


# --- identifiability ----------------------------------------------------------- #
def test_simulator_columns_and_designs():
    sim = ci.CommonsSimulator(SMALL, {"mode": "introduce", "seed_index": 0}, n_steps=100, waves=2)
    assert sim.times == [50, 100]
    assert len(sim.summary_names) == 2 * 2 * 2                # waves x (adoption, shortfall) x groups
    assert sim.design_columns("survey") == ["adoption_w2_A", "adoption_w2_B"]
    assert sim.design_columns("survey+water") == ["adoption_w2_A", "adoption_w2_B",
                                                  "shortfall_w2_A", "shortfall_w2_B"]
    assert len(sim.design_columns("panel")) == 4 and len(sim.design_columns("panel+water")) == 8
    with pytest.raises(ValueError, match="unknown design"):
        sim.design_columns("census")
    with pytest.raises(ValueError, match="unknown parameter"):
        ci.CommonsSimulator(SMALL, parameters=("theta", "sigma"))


def test_simulator_is_reproducible_and_reads_parameters():
    sim = ci.CommonsSimulator(SMALL, {"mode": "introduce", "seed_index": 0}, n_steps=100, waves=2)
    p = {"theta": 1.5, "gamma_share": 0.0, "lambda0": 4.0}
    a, b = sim(p, 7), sim(p, 7)
    np.testing.assert_array_equal(a, b)
    assert np.all((a >= 0) & (a <= 1))
    sf = [sim.summary_names.index(f"shortfall_w2_{g}") for g in ("A", "B")]
    c = sim(dict(p, gamma_share=2.0), 7)
    assert c[sf[0]] < c[sf[1]]                                  # A is powerful


def test_survey_answers_are_samples():
    sim = ci.CommonsSimulator(SMALL, {"mode": "all"}, n_steps=100, waves=2, n_respondents=10)
    x = sim({"theta": 1.5, "gamma_share": 1.0, "lambda0": 4.0}, 3)
    ad = [x[sim.summary_names.index(f"adoption_w2_{g}")] for g in ("A", "B")]
    assert all(abs(v * 10 - round(v * 10)) < 1e-9 for v in ad)  # k out of 10 respondents


def test_identify_designs_shares_one_table():
    sim = ci.CommonsSimulator(SMALL, {"mode": "introduce", "seed_index": 0}, n_steps=100,
                              waves=2, parameters=("theta", "gamma_share"))
    reports, table = ci.identify_designs(sim, ("survey", "survey+water"), n_reference=160,
                                         n_test=20, accept=0.2, seed=1)
    assert set(reports) == {"survey", "survey+water"} and len(table) == 160
    for r in reports.values():
        assert [p["name"] for p in r.parameters] == ["theta", "gamma_share"]
    # water records measure the shares directly
    g = {d: {p["name"]: p["contraction"] for p in r.parameters}["gamma_share"]
         for d, r in reports.items()}
    assert g["survey+water"] > g["survey"]
    text = ci.designs_report(reports, sim)
    assert "| survey+water |" in text and "gamma_share contraction" in text


def test_identify_command(tmp_path, capsys):
    cfg = tmp_path / "small.json"
    cfg.write_text(json.dumps(SMALL))
    args = [str(cfg), "--seed-group", "A", "--n-reference", "80", "--n-test", "10",
            "--accept", "0.25", "--steps", "100", "--waves", "2", "--cores", "1",
            "--designs", "survey,survey+water", "--params", "theta,gamma_share",
            "--outdir", str(tmp_path)]
    assert commons_main(["identify", *args]) == 0
    stem = tmp_path / "identify-small-introduce-A-scarcity-waves2-steps100"
    for ext in ("_report.md", "_report.json", "_table.npz"):
        assert (tmp_path / (stem.name + ext)).exists()
    assert commons_main(["identify", *args, "--reuse"]) == 0
    assert "reusing 80 simulations" in capsys.readouterr().out


def test_identify_command_errors(capsys):
    assert commons_main(["identify", "--seed-group", "Nowhere"]) == 2
    assert "no group 'Nowhere'" in capsys.readouterr().err
    assert commons_main(["identify", "--designs", "census"]) == 2
    assert "unknown design" in capsys.readouterr().err
    assert commons_main(["identify", "--set", "learning.theta=2"]) == 2
    assert "being recovered" in capsys.readouterr().err
