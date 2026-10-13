"""miras.commons 0.2.2: adoption in each group for scenarios, parameter
overrides (--set), the seed in output names, and replication checks in
`analyze`."""
import csv
import json

import numpy as np
import pytest

from miras.commons import analysis
from miras.commons import experiments as ex
from miras.commons.cli import main as commons_main, run_tag

SMALL = {
    "groups": [{"name": "A", "size": 60, "tightness": 0.1, "power": 2.0},
               {"name": "B", "size": 40, "tightness": 0.9},
               {"name": "C", "size": 50, "parochialism": 0.9}],
    "resource": {"rho": 0.7},
    "timings": ["scarcity"],
}


# --- adoption in each group ---------------------------------------------------- #
def test_scenario_outcomes_include_each_group():
    names = ex.outcome_names(SMALL)
    assert names[:len(ex.OUTCOMES)] == ex.OUTCOMES
    assert names[len(ex.OUTCOMES):] == ("adoption_A", "adoption_B", "adoption_C")
    assert ex.outcome_names(None) == ex.OUTCOMES          # E1 is unchanged


def test_group_adoption_adds_up_to_overall_adoption():
    cells = ex.scenario_cells(SMALL)
    out = ex.run_cells(cells, 2, seed=3, steps=150, base=ex.base_settings(), config=SMALL)
    names = ex.outcome_names(SMALL)
    sizes = np.array([g["size"] for g in SMALL["groups"]], float)
    per_group = out[..., len(ex.OUTCOMES):]
    assert np.all((per_group >= 0) & (per_group <= 1))
    overall = per_group @ sizes / sizes.sum()
    np.testing.assert_allclose(overall, out[..., names.index("mean_adoption_last")], atol=1e-9)


def test_group_columns_do_not_change_the_other_outcomes():
    """Same seed, same numbers as 0.2.1: the extra columns are computed from
    the same runs and draw no random numbers."""
    cells = ex.scenario_cells(SMALL)
    with_groups = ex.run_cells(cells, 2, seed=5, steps=120, base=ex.base_settings(), config=SMALL)
    for k, cell in enumerate(cells):
        model, sd = ex.build_scenario(cell, SMALL, ex.base_settings())
        seeds = np.random.SeedSequence(5).generate_state(len(cells) * 2, dtype=np.uint64) % (2**63)
        o = model.run(120, sd, seed=int(seeds[2 * k])).outcomes()
        np.testing.assert_allclose(with_groups[k, 0, :len(ex.OUTCOMES)],
                                   [float(o[n]) for n in ex.OUTCOMES])


def test_scenario_report_has_group_table():
    cells = ex.scenario_cells(SMALL)
    out = ex.run_cells(cells, 2, seed=1, steps=100, base=ex.base_settings(), config=SMALL)
    rows = ex.summarise(cells, out, ex.outcome_names(SMALL))
    report = ex.scenario_report(rows, SMALL)
    assert "Adoption in each group" in report
    assert "| seeding | A | B | C | shortage | sustained |" in report
    assert "| A originate |" in report and "| every group |" in report


def test_scenario_command_writes_group_columns(tmp_path, capsys):
    cfg = tmp_path / "small.json"
    cfg.write_text(json.dumps(SMALL))
    assert commons_main(["scenario", str(cfg), "--reps", "2", "--steps", "60", "--cores", "1",
                         "--outdir", str(tmp_path)]) == 0
    with open(tmp_path / "scenario-small-steps60_runs.csv") as fh:
        header = next(csv.reader(fh))
    assert header[-3:] == ["adoption_A", "adoption_B", "adoption_C"]
    assert "Adoption in each group" in capsys.readouterr().out


# --- parameter overrides ------------------------------------------------------- #
def test_parse_sets_types_and_errors():
    sets = ex.parse_sets(["learning.theta=2", "learning.n_conform=5",
                          "innovation.efficiency=false", "resource.storage=10"])
    assert sets == {"learning": {"theta": 2.0, "n_conform": 5},
                    "innovation": {"efficiency": False}, "resource": {"storage": 10.0}}
    assert isinstance(sets["learning"]["n_conform"], int)
    assert ex.parse_sets([]) == {}
    for bad, msg in [("theta=2", "section.field=value"), ("learn.theta=2", "unknown section"),
                     ("learning.thetaa=2", "no field 'thetaa'"),
                     ("learning.n_conform=2.5", "not a valid int"),
                     ("innovation.efficiency=maybe", "not a valid bool")]:
        with pytest.raises(ValueError, match=msg):
            ex.parse_sets([bad])


def test_sets_reach_the_model():
    base = ex.base_settings(sets=ex.parse_sets(["learning.theta=2.5", "innovation.cost=0.2",
                                                "resource.storage=7"]))
    cell = ex.e1_cells(rho=[0.7])[3]
    model, _ = ex.build(cell, base)
    assert model.lrn.theta == 2.5 and model.inn.cost == 0.2
    assert model.res.storage == 7 and model.res.rho == 0.7
    with pytest.raises(ValueError, match="--rho"):
        ex.base_settings(sets={"resource": {"rho": 0.8}})


def test_sets_change_results_and_defaults_do_not():
    cell = ex.e1_cells(rho=[0.7], contact=[0.1], timing=["scarcity"])[1]      # every group seeded
    default = ex.build(cell, ex.base_settings())[0].run(200, ex.build(cell)[1], seed=1).outcomes()
    same = ex.build(cell, ex.base_settings(sets=ex.parse_sets(["learning.theta=1.5"])))[0] \
        .run(200, ex.build(cell)[1], seed=1).outcomes()
    other = ex.build(cell, ex.base_settings(sets=ex.parse_sets(["innovation.cost=0.6"])))[0] \
        .run(200, ex.build(cell)[1], seed=1).outcomes()
    assert same == default
    assert other["mean_adoption_last"] < default["mean_adoption_last"]


def test_apply_sets_to_a_scenario():
    cfg = ex.apply_sets(SMALL, ex.parse_sets(["resource.rho=0.85", "learning.theta=2"]))
    assert cfg["resource"] == {"rho": 0.85} and cfg["learning"] == {"theta": 2.0}
    assert SMALL["resource"] == {"rho": 0.7} and "learning" not in SMALL   # original untouched


# --- output names -------------------------------------------------------------- #
def test_run_tag():
    assert run_tag("e1-rho0.7") == "e1-rho0.7"                             # as in 0.2.1
    assert run_tag("e1-rho0.7", off=("power_share",)) == "e1-rho0.7-off-power_share"
    assert run_tag("e1-rho0.7", seed=2) == "e1-rho0.7-seed2"
    sets = ex.parse_sets(["learning.theta=2", "learning.beta_s=5"])
    assert run_tag("e1", ("tight_conformity",), sets, 3) == \
        "e1-off-tight_conformity-set-theta2-beta_s5-seed3"
    assert run_tag("e1-rho0.7", support=False) == "e1-rho0.7-nosupport"
    assert run_tag("scenario-x", seed=2, steps=1500) == "scenario-x-steps1500-seed2"


def test_no_support_removes_subsidy_and_demonstrators():
    cell = dict(ex.e1_cells(rho=[0.7], contact=[0.1], timing=["scarcity"])[3], mode="introduce")
    _, with_support = ex.build(cell, ex.base_settings())
    _, without = ex.build(cell, ex.base_settings(support=False))
    assert with_support.support and not without.support
    _, sd = ex.build_scenario({"mode": "introduce", "seed_index": 1, "timing": "scarcity"},
                              SMALL, ex.base_settings(support=False))
    assert not sd.support and sd.group == 1


@pytest.mark.filterwarnings("ignore::RuntimeWarning")   # the E1 report of a 6-cell subset
def test_e1_command_names_seed_and_sets(tmp_path, capsys, monkeypatch):
    few = ex.e1_cells(rho=[0.7], contact=[0.1], timing=["scarcity"])[:6]
    monkeypatch.setattr(ex, "e1_cells", lambda **kw: few)          # keep the test fast
    assert commons_main(["e1", "--quick", "--rho", "0.7", "--contact", "0.1", "--timing", "scarcity",
                         "--cores", "1", "--seed", "2", "--set", "learning.theta=2",
                         "--outdir", str(tmp_path)]) == 0
    assert (tmp_path / "e1-rho0.7-contact0.1-timingscarcity-quick-set-theta2-seed2_summary.csv").exists()


def test_bad_set_on_the_command_line(capsys):
    assert commons_main(["e1", "--quick", "--set", "learning.thetaa=2"]) == 2
    assert "no field 'thetaa'" in capsys.readouterr().err
    assert commons_main(["e1", "--quick", "--set", "resource.rho=0.8"]) == 2
    assert "--rho" in capsys.readouterr().err


# --- replication in analyze ---------------------------------------------------- #
def _summary(path, cells, seed):
    out = ex.run_cells(cells, 4, seed=seed, steps=40, base=ex.base_settings())
    ex.write_summary(path, ex.summarise(cells, out))


def test_same_named_summaries_are_kept_apart_and_compared(tmp_path):
    cells = ex.e1_cells(rho=[0.7], contact=[0.1], timing=["scarcity"])[:20]
    (tmp_path / "s1").mkdir()
    (tmp_path / "s2").mkdir()
    a, b = tmp_path / "s1" / "e1-x_summary.csv", tmp_path / "s2" / "e1-x_summary.csv"
    _summary(a, cells, 1)
    _summary(b, cells, 2)
    assert analysis.run_names([str(a), str(b)]) == ["s1/e1-x", "s2/e1-x"]
    report = analysis.analyze([str(a), str(b)])
    assert "`s1/e1-x`" in report and "`s2/e1-x`" in report
    assert "## Cell-by-cell agreement with the first run" in report
    assert "| s2/e1-x | 20 |" in report


def test_agreement_of_a_run_with_itself(tmp_path):
    cells = ex.e1_cells(rho=[0.7], contact=[0.1], timing=["scarcity"])[:20]
    a = tmp_path / "e1-a_summary.csv"
    _summary(a, cells, 1)
    b = tmp_path / "e1-b_summary.csv"
    b.write_text(a.read_text())
    rows = analysis.agreement({"a": analysis.read_summary(a), "b": analysis.read_summary(b)}, [0.7])
    line = [r for r in rows if r.startswith("| b |")][0]
    assert "| 0.000 |" in line and "| 0% |" in line
