"""miras.commons 0.2.1: one-attribute backgrounds, condition filters, scenario
validation, the example scenario, continuous outcomes and the analysis report."""
import json

import numpy as np
import pytest

from miras.commons import CommonsModel, Group, Resource, Seeding
from miras.commons import analysis
from miras.commons import experiments as ex
from miras.commons.cli import main as commons_main


# --- backgrounds and filters ------------------------------------------------- #
def test_parse_background():
    assert ex.parse_background("low") == {k: "low" for k in ex.LEVELS}
    one = ex.parse_background("tightness=low")
    assert one["tightness"] == "low" and all(v == "mid" for k, v in one.items() if k != "tightness")
    two = ex.parse_background("tightness=low, power=high")
    assert (two["tightness"], two["power"]) == ("low", "high")
    assert ex.background_label(two) == "tightness-low+power-high"
    assert ex.background_label(ex.parse_background("mid")) == "mid"
    for bad in ("tightnes=low", "tightness=lowest", "tightness"):
        with pytest.raises(ValueError):
            ex.parse_background(bad)


def test_one_attribute_background_changes_only_that_attribute():
    cell = ex.e1_cells(background="tightness=low")[5]
    model, _ = ex.build(cell)
    bg = model.groups[1]
    assert bg.tightness == 0.1 and bg.altruism == 0.5 and bg.wealth == 1.0 and bg.power == 1.0


def test_condition_filters():
    assert len(ex.e1_cells()) == 8 * 488
    severe = ex.e1_cells(rho=[0.7])
    assert len(severe) == 4 * 488 and {c["rho"] for c in severe} == {0.7}
    one = ex.e1_cells(rho=[0.7], contact=[0.3], timing=["scarcity"])
    assert len(one) == 488
    with pytest.raises(ValueError):
        ex.e1_cells(timing=["later"])


def test_cells_from_0_2_0_still_build():
    cell = dict(ex.e1_cells()[5])
    for k in ex.LEVELS:
        cell.pop(f"bg_{k}")                    # a 0.2.0 summary row has only 'background'
    model, _ = ex.build(cell)
    assert model.groups[1].tightness == 0.5


# --- continuous outcomes -------------------------------------------------------- #
def test_adoption_gap_outcome():
    m = CommonsModel([Group(name=f"g{i}", size=100) for i in range(3)], resource=Resource(rho=0.7))
    o = m.run(100, Seeding(mode="none"), seed=1).outcomes()
    assert o["a_star"] == pytest.approx(0.75)
    assert o["adoption_gap"] == pytest.approx(-0.75)
    assert set(ex.OUTCOMES) <= set(o)


# --- scenarios -------------------------------------------------------------------- #
def test_example_scenario_is_valid(tmp_path):
    path = tmp_path / "groups.json"
    path.write_text(ex.example_scenario_json())
    cfg = ex.load_config(str(path))
    assert [g["name"] for g in cfg["groups"]] == ["Highland", "Valley", "Riverside"]


@pytest.mark.parametrize("content, message", [
    (None, "not found"),
    ("{not json", "not valid JSON"),
    (json.dumps({"groups": []}), "non-empty"),
    (json.dumps({"groups": [{"name": "A", "tightnes": 0.5}]}), "unknown field"),
    (json.dumps({"groups": [{"name": "A"}], "resorce": {}}), "unknown top-level"),
    (json.dumps({"groups": [{"name": "A"}, {"name": "A"}]}), "unique"),
    (json.dumps({"groups": [{"name": "A"}], "timings": ["later"]}), "timings"),
    (json.dumps({"groups": [{"name": "A"}], "resource": {"rho": 0.7, "depth": 3}}), "unknown field"),
])
def test_scenario_errors_explain_the_problem(tmp_path, content, message):
    path = tmp_path / "s.json"
    if content is not None:
        path.write_text(content)
    with pytest.raises(ex.ScenarioError, match=message):
        ex.load_config(str(path))


def test_scenario_cli_error_is_one_line(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert commons_main(["scenario", "groups.json"]) == 2
    err = capsys.readouterr().err
    assert err.startswith("error: scenario file 'groups.json' not found")
    assert "miras commons example > groups.json" in err and "Traceback" not in err


def test_example_command(capsys):
    assert commons_main(["example"]) == 0
    assert json.loads(capsys.readouterr().out)["groups"][0]["name"] == "Highland"


def test_bad_background_on_the_command_line(capsys):
    assert commons_main(["e1", "--background", "tightness=lowest", "--quick"]) == 2
    assert "unknown level" in capsys.readouterr().err


# --- analysis ------------------------------------------------------------------------ #
def _summary(tmp_path, name, off=()):
    cells = [dict(c, size=40) for c in ex.e1_cells(rho=[0.7], contact=[0.3], timing=["scarcity"])]
    cells = [c for c in cells if c["mode"] in ("none", "all") or
             (c["seed_altruism"] == 0.5 and c["seed_parochialism"] == 0.5 and c["seed_wealth"] == 1.0)]
    out = ex.run_cells(cells, 2, steps=40, base=ex.base_settings(off))
    path = tmp_path / f"{name}_summary.csv"
    ex.write_summary(path, ex.summarise(cells, out))
    return str(path)


def test_analysis_report_sections(tmp_path):
    a = _summary(tmp_path, "e1")
    b = _summary(tmp_path, "e1-off-power_share", off=("power_share",))
    report = analysis.analyze([a, b])
    for heading in ("## Overview", "### Main effects", "### Where adoption happens",
                    "### Sustained share by seed tightness and power", "### Introduce minus originate",
                    "### Best seed groups", "## Comparison across runs", "Effect (high minus low) on mean adoption"):
        assert heading in report, heading
    assert "| e1 | 0.7 |" in report and "e1-off-power_share" in report


def test_analysis_reads_0_2_0_summaries(tmp_path):
    path = _summary(tmp_path, "old")
    import csv
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    drop = [k for k in rows[0] if k.startswith(("a_star", "adoption_gap"))]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[k for k in rows[0] if k not in drop])
        w.writeheader()
        w.writerows({k: v for k, v in r.items() if k not in drop} for r in rows)
    rows = analysis.read_summary(path)
    assert rows[0]["a_star"] == pytest.approx(0.75)
    assert np.isfinite(rows[0]["adoption_gap"])


def test_analyze_command(tmp_path, capsys):
    a = _summary(tmp_path, "e1")
    out = tmp_path / "report.md"
    assert commons_main(["analyze", a, "--out", str(out)]) == 0
    assert out.read_text().startswith("# miras.commons analysis")
    assert commons_main(["analyze", str(tmp_path / "missing_summary.csv")]) == 2
