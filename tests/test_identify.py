"""Detector sensitivity and specificity against toy simulators with known
identifiability. A detector that fires on everything is worse than none, so
every detector is tested in both directions."""
import numpy as np
import pytest

from miras import FunctionSimulator, Thresholds, Uniform, analyze, identify
from miras.inference.abc import Posterior

import toys

AB = {"a": Uniform(0.2, 1), "b": Uniform(0.2, 1)}
ABC_ = {**AB, "c": Uniform(0, 1)}


def run(fn, priors=AB, seed=1, **kw):
    return identify(FunctionSimulator(fn), priors, n_reference=4000, n_test=60, seed=seed, **kw)


def ids(report):
    return sorted((f.id, tuple(f.params)) for f in report.findings)


# --- sensitivity ------------------------------------------------------------ #
@pytest.mark.parametrize("fn", [toys.product, toys.total, toys.ratio])
def test_equifinality_detected(fn):
    assert ids(run(fn)) == [("EQUIFINALITY", ("a", "b"))]


def test_equifinality_direction_has_right_sign():
    prod = next(f for f in run(toys.product).findings if f.id == "EQUIFINALITY")
    ratio = next(f for f in run(toys.ratio).findings if f.id == "EQUIFINALITY")
    assert prod.evidence["slope_u"] < 0 < ratio.evidence["slope_u"]
    assert "lowering" in prod.what and "raising b" in ratio.what


def test_not_identified_detected():
    assert ids(run(toys.irrelevant_c, ABC_)) == [("NOT_IDENTIFIED", ("c",))]


def test_equifinal_pair_found_among_three_parameters():
    assert ids(run(toys.product_plus_c, ABC_)) == [("EQUIFINALITY", ("a", "b"))]


# --- specificity ------------------------------------------------------------ #
@pytest.mark.parametrize("fn", [toys.identified, toys.weak_b, toys.correlated])
def test_quiet_when_identified(fn):
    report = run(fn)
    assert report.findings == [] and report.ok


def test_calibration_of_identified_problem():
    report = run(toys.identified)
    for p in report.parameters:
        assert p["contraction"] > 0.9
        assert 0.8 <= p["coverage90"] <= 1.0
        assert abs(p["bias"]) < 0.1


def test_equifinal_parameters_not_double_reported_as_not_identified():
    # a and b each have low marginal contraction under a product, but the joint
    # is informative: that is equifinality, not absence of information.
    assert all(f.id != "NOT_IDENTIFIED" for f in run(toys.product).findings)


# --- analyze() works with posteriors from any backend ----------------------- #
def test_analyze_with_external_posteriors():
    rng = np.random.default_rng(0)
    truths = rng.uniform(0.2, 1, (20, 2))
    posts = []
    for t in truths:  # an "external" sampler that nails a but returns the prior for b
        U = np.column_stack([rng.normal(t[0], 0.01, 500), rng.uniform(0.2, 1, 500)])
        posts.append(Posterior(AB, U, np.ones(500)))
    report = analyze(AB, truths, posts, info={"method": "external"})
    assert ids(report) == [("NOT_IDENTIFIED", ("b",))]


def test_thresholds_are_configurable():
    strict = Thresholds(not_identified=0.99)
    report = run(toys.identified, thresholds=strict)
    assert {f.id for f in report.findings} == {"NOT_IDENTIFIED"}


def test_report_outputs(tmp_path):
    report = run(toys.product)
    assert "EQUIFINALITY" in report.summary() and "EQUIFINALITY" in report.to_markdown()
    d = report.to_dict()
    assert d["findings"][0]["id"] == "EQUIFINALITY" and len(d["parameters"]) == 2
    report.to_json(tmp_path / "r.json")
    pytest.importorskip("matplotlib")
    report.plot(tmp_path / "r.png")
    assert (tmp_path / "r.png").stat().st_size > 1000


def test_smc_method_runs():
    report = identify(FunctionSimulator(toys.product), AB, method="smc", n_test=3, seed=2,
                      smc={"n_particles": 150, "n_generations": 4})
    assert report.info["method"] == "smc" and report.info["n_simulations"] > 0


def test_regional_not_identified_has_a_where():
    # b is informative only when a < 0.5: globally averaged, b looks half
    # identified; the finding must say where it fails.
    report = identify(FunctionSimulator(toys.b_only_when_a_low), {"a": Uniform(0, 1), "b": Uniform(0, 1)},
                      n_reference=4000, n_test=90, seed=3)
    f = [x for x in report.findings if x.id == "NOT_IDENTIFIED"]
    assert len(f) == 1 and f[0].params == ["b"]
    assert f[0].where.startswith("a >")
    assert float(f[0].where.split(">")[1]) > 0.5


def test_global_findings_have_no_where():
    f = run(toys.irrelevant_c, ABC_).findings[0]
    assert f.where == ""
