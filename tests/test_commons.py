"""miras.commons: the verification checks V1-V9 of the specification, plus
tests of the grouped-population engine and the experiment runner.

Each V-test compares the model with a result that is known without it.
"""
import math

import numpy as np
import pytest

from miras.commons import (CommonsModel, Group, Innovation, Learning, Mechanisms, Resource,
                           Seeding)
from miras.commons import experiments as ex
from miras.engine.groups import GroupedPopulation, water_fill

NO_NORMS = dict(tightness=0.0, altruism=0.0, parochialism=0.0)


def one_group(size=2000, **kw):
    return [Group(name="only", size=size, **{**NO_NORMS, **kw})]


# --------------------------------------------------------------------------- #
# V1-V3: the resource
# --------------------------------------------------------------------------- #
def test_v1_stock_drains_linearly_then_shortage_is_one_minus_rho():
    groups = [Group(name=f"g{i}", size=200) for i in range(5)]
    res = Resource(rho=0.85, storage=17.0)
    r = CommonsModel(groups, resource=res).run(200, Seeding(mode="none", timing="plenty"), seed=1)
    N, D = 1000, 1000.0
    I = 0.85 * N
    K = 17.0 * I
    first = math.floor((K - D) / (D - I)) + 1             # exact first shortage step
    assert np.all(r.shortage[:first] == 0) and r.shortage[first] > 0
    np.testing.assert_allclose(np.diff(r.stock[:first]), -(D - I) / K)
    np.testing.assert_allclose(r.shortage[first + 1:], 1 - 0.85)
    assert np.all(r.adoption == 0)
    # rho >= 1: never a shortage
    r2 = CommonsModel(groups, resource=Resource(rho=1.0)).run(200, Seeding(mode="none", timing="plenty"), seed=1)
    assert np.all(r2.shortage == 0)


@pytest.mark.parametrize("rho, sustained", [(0.65, True), (0.55, False)])
def test_v2_universal_adoption_sustains_iff_rho_at_least_one_minus_delta(rho, sustained):
    groups = [Group(name=f"g{i}", size=100) for i in range(3)]
    m = CommonsModel(groups, innovation=Innovation(saving=0.4), resource=Resource(rho=rho),
                     learning=Learning(p_learn=0.0))
    r = m.run(400, Seeding(mode="all", fraction=1.0, timing="plenty"), seed=2)
    assert np.all(r.adoption == 1)
    o = r.outcomes()
    assert o["sustained"] is sustained
    if not sustained:                                      # demand 0.6 N d0 exceeds recharge
        assert r.shortage[-1] == pytest.approx(1 - rho / 0.6)


def test_v3_water_fill_conserves_caps_and_weights():
    rng = np.random.default_rng(3)
    for _ in range(200):
        caps = rng.uniform(0, 5, 7)
        w = rng.uniform(0.1, 3, 7)
        total = rng.uniform(0, caps.sum() * 1.2)
        x = water_fill(total, caps, w)
        assert x.sum() == pytest.approx(min(total, caps.sum()))
        assert np.all(x <= caps + 1e-9) and np.all(x >= -1e-12)
        unfilled = x < caps - 1e-9                          # uncapped claimants: proportional
        if unfilled.sum() > 1:
            ratio = x[unfilled] / w[unfilled]
            assert np.ptp(ratio) < 1e-8


def test_v3_power_share_in_a_shortage():
    groups = [Group(name="strong", size=200, power=2.0), Group(name="weak", size=200, power=1.0)]
    # gamma = 1: entitlements 2:1; the strong group is capped at its demand
    r = CommonsModel(groups).run(5, Seeding(mode="none", timing="scarcity"), seed=4)
    np.testing.assert_allclose(r.payoff[-1], [1.0, 0.7])   # 340 water: 200 + 140
    # gamma = 0 (power_share off): equal quotas across groups
    m = CommonsModel(groups, mechanisms=Mechanisms().without("power_share"))
    r0 = m.run(5, Seeding(mode="none", timing="scarcity"), seed=4)
    np.testing.assert_allclose(r0.payoff[-1], [0.85, 0.85])


# --------------------------------------------------------------------------- #
# V4-V6: learning
# --------------------------------------------------------------------------- #
def test_v4_plentiful_water_adoption_declines_as_replicator_predicts():
    # adopter payoff 0.9, non-adopter 1.0; switch prob = min(1, beta_s * 0.1) = 1
    L = Learning(mu=0.0, p_learn=0.1)
    m = CommonsModel(one_group(), resource=Resource(rho=2.0), learning=L)
    r = m.run(40, Seeding(mode="originate", fraction=0.5, timing="plenty"), seed=5)
    f, pred = 0.5, []
    for _ in range(40):
        f = f - L.p_learn * f * (1 - f) * min(1.0, L.beta_s * 0.1)
        pred.append(f)
    assert np.max(np.abs(r.adoption[:, 0] - pred)) < 0.02


def test_v5_rationing_raises_adoption_until_shortage_equals_cost():
    kappa, rho, delta = 0.1, 0.85, 0.4
    m = CommonsModel(one_group(), innovation=Innovation(cost=kappa, saving=delta),
                     resource=Resource(rho=rho), learning=Learning(mu=0.0),
                     mechanisms=Mechanisms().without("ingroup_value"))
    r = m.run(600, Seeding(mode="originate", fraction=0.02, timing="scarcity"), seed=6)
    a_eq = (1 - rho / (1 - kappa)) / delta                  # shortage = kappa
    assert r.adoption[-200:, 0].mean() == pytest.approx(a_eq, abs=0.03)
    assert r.shortage[-200:].mean() == pytest.approx(kappa, abs=0.02)


@pytest.mark.parametrize("start, end", [(0.3, 0.0), (0.7, 1.0)])
def test_v6_conformity_alone_removes_minorities_and_fixes_majorities(start, end):
    m = CommonsModel(one_group(size=500, tightness=1.0), resource=Resource(rho=2.0),
                     learning=Learning(mu=0.0),
                     mechanisms=Mechanisms().without("tight_sanctions", "tight_caution"))
    r = m.run(400, Seeding(mode="originate", fraction=start, timing="plenty"), seed=7)
    assert r.adoption[-1, 0] == end


# --------------------------------------------------------------------------- #
# V7-V9: symmetry and bookkeeping
# --------------------------------------------------------------------------- #
def test_v7_seed_group_does_not_matter_when_groups_are_identical():
    groups = [Group(name=f"g{i}", size=150, tightness=0.1, altruism=0.9) for i in range(4)]
    m = CommonsModel(groups)
    a = [m.run(300, Seeding(group=0), seed=s).overall[-50:].mean() for s in range(20)]
    b = [m.run(300, Seeding(group=3), seed=100 + s).overall[-50:].mean() for s in range(20)]
    se = math.sqrt(np.var(a, ddof=1) / 20 + np.var(b, ddof=1) / 20)
    assert abs(np.mean(a) - np.mean(b)) < 3 * se + 0.02


def test_v8_fully_parochial_groups_never_take_up_the_trait():
    groups = [Group(name=f"g{i}", size=150, tightness=0.1, altruism=0.9, parochialism=1.0,
                    contact=0.5) for i in range(4)]
    m = CommonsModel(groups, learning=Learning(mu=0.0))
    r = m.run(300, Seeding(mode="originate", group=1, fraction=0.3), seed=8)
    assert r.adoption[:, 1].max() > 0
    assert np.all(r.adoption[:, [0, 2, 3]] == 0)


def test_v9_same_seed_same_result():
    m = CommonsModel([Group(name=f"g{i}", size=100) for i in range(3)])
    r1 = m.run(100, Seeding(mode="introduce"), seed=9)
    r2 = m.run(100, Seeding(mode="introduce"), seed=9)
    np.testing.assert_array_equal(r1.adoption, r2.adoption)
    np.testing.assert_array_equal(r1.stock, r2.stock)


def test_v9_resumed_experiment_is_identical(tmp_path):
    cells = [c for c in ex.e1_cells() if c["rho"] == 0.85 and c["contact"] == 0.1][:4]
    cells = [dict(c, size=40) for c in cells]
    base = ex.base_settings()
    full = ex.run_cells(cells, 3, steps=30, base=base)
    done = np.zeros(12, bool)
    done[::2] = True
    partial = np.full_like(full, np.nan)
    for k in np.flatnonzero(done):
        partial[k // 3, k % 3] = full[k // 3, k % 3]
    ck = ex.Checkpoint(tmp_path / "c.npz", {"t": 1})
    ck.save(out=partial, done=done)
    resumed = ex.run_cells(cells, 3, steps=30, base=base, checkpoint=ck)
    np.testing.assert_array_equal(resumed, full)


# --------------------------------------------------------------------------- #
# Engine and experiment plumbing
# --------------------------------------------------------------------------- #
def test_grouped_population_model_choice():
    rng = np.random.default_rng(10)
    pop = GroupedPopulation([100, 300, 50], rng)
    focal = np.repeat(np.arange(100), 100)                  # all in group 0
    src, looked, kept = pop.choose_model_groups(focal, [1.0, 1.0, 1.0], [1.0, 1.0, 1.0])
    assert looked.all() and np.mean(src == 1) == pytest.approx(300 / 350, abs=0.02)
    src, _, kept = pop.choose_model_groups(focal, [1.0, 0, 0], [1, 1, 1], filter_out=[0.75, 0, 0])
    assert kept.mean() == pytest.approx(0.25, abs=0.02)
    m = pop.sample_in_group(np.array([0, 150, 420]), 500)
    assert all(np.all(pop.group[m[i]] == pop.group[f]) for i, f in enumerate([0, 150, 420]))
    with pytest.raises(ValueError):
        GroupedPopulation([10, 0], rng)


def test_no_innovation_reference_has_no_adopters():
    m = CommonsModel([Group(name=f"g{i}", size=100, tightness=0.1) for i in range(3)])
    for timing in ("plenty", "scarcity"):
        r = m.run(200, Seeding(mode="none", timing=timing), seed=11)
        assert np.all(r.adoption == 0)


def test_ownership_bias_slows_introduction_in_a_parochial_seed_group():
    g = [Group(name=f"g{i}", size=200, tightness=0.1, altruism=0.9, parochialism=0.9)
         for i in range(3)]
    m = CommonsModel(g)
    orig = np.mean([m.run(200, Seeding(mode="originate", support=False), seed=s).adoption[-1, 0]
                    for s in range(8)])
    intro = np.mean([m.run(200, Seeding(mode="introduce", support=False), seed=s).adoption[-1, 0]
                     for s in range(8)])
    assert orig > intro


def test_e1_design_size_and_cells_build():
    cells = ex.e1_cells()
    assert len(cells) == 8 * (2 + 243 * 2)                  # conditions x (refs + profiles x modes)
    model, sd = ex.build(cells[5], ex.base_settings())
    assert len(model.groups) == 5 and sd.group == 0
    with pytest.raises(KeyError):
        ex.base_settings(off=("no_such_mechanism",))


def test_scenario_cells_and_report(tmp_path):
    cfg = {"groups": [{"name": "A", "size": 60, "power": 2.0},
                      {"name": "B", "size": 40, "tightness": 0.9}],
           "timings": ["scarcity"]}
    cells = ex.scenario_cells(cfg)
    assert len(cells) == 2 + 2 * 2
    out = ex.run_cells(cells, 2, steps=20, base=ex.base_settings(), config=cfg)
    rows = ex.summarise(cells, out)
    report = ex.scenario_report(rows, cfg)
    assert "(no innovation)" in report and "| A |" in report


def test_reference_doc_matches_code():
    """docs/commons-model.md lists the code's defaults; regenerate it with
    `python docs/_generate_commons_model.py` after changing a default."""
    import dataclasses
    import pathlib
    from miras.commons.model import Group, Innovation, Learning, Mechanisms, Resource, Seeding
    doc = pathlib.Path(__file__).resolve().parents[1] / "docs" / "commons-model.md"
    if not doc.exists():
        pytest.skip("docs/ not present (installed package)")
    text = doc.read_text()
    for cls in (Group, Innovation, Resource, Learning, Mechanisms, Seeding):
        for f in dataclasses.fields(cls):
            assert f"| `{f.name}` | `{f.default!r}` |" in text, f"{cls.__name__}.{f.name} is stale"
