"""The engine against analytic results that do not depend on it."""
import numpy as np
import pytest

from miras import Conformity, Islands, Model, Neutral, PayoffBias, WrightFisher, theory


def wf(n_groups, group_size, **kw):
    kw.setdefault("learning", Neutral())
    kw.setdefault("n_models", 1)
    return Model(structure=Islands(n_groups, group_size), demography=WrightFisher(), **kw)


def test_neutral_homozygosity_matches_exact_recursion():
    N, mu = 100, 0.02
    r = wf(1, N, innovation=mu).simulate(12000, seed=1, record=("within_diversity",))
    sim = 1 - r.series["within_diversity"][1000:].mean()
    assert sim == pytest.approx(theory.expected_homozygosity(N, mu), rel=0.05)


def test_number_of_variants_matches_ewens():
    N, mu = 100, 0.02
    r = wf(1, N, innovation=mu).simulate(12000, seed=2, record=("total_variants",))
    sim = r.series["total_variants"][1000:].mean()
    # Ewens is a diffusion approximation: agreement to ~10% at N = 100
    assert sim == pytest.approx(theory.ewens_expected_variants(N, mu), rel=0.10)


@pytest.mark.parametrize("d, gs, m, mu", [(20, 50, 0.05, 0.01), (10, 100, 0.02, 0.02),
                                          (30, 50, 0.2, 0.02)])
def test_island_model_fst(d, gs, m, mu):
    r = wf(d, gs, migration=m, innovation=mu, n_models=5).simulate(2500, seed=3)
    assert r.series["fst"][500:].mean() == pytest.approx(theory.expected_fst(gs, d, m, mu), rel=0.06)


def test_island_theory_reduces_to_single_population():
    N, mu = 80, 0.03
    F0, _ = theory.island_identity(N, 1, 0.0, mu)
    assert 1 / N + (1 - 1 / N) * F0 == pytest.approx(theory.expected_homozygosity(N, mu))


HAWK_DOVE = ((-0.5, 2.0), (0.0, 1.0))        # V = 2, C = 3: mixed equilibrium p_hawk = 2/3


def test_payoff_bias_follows_replicator_dynamics():
    hawk = lambda t, g: float(np.mean(t == 0))
    m = wf(1, 20000, learning=PayoffBias(HAWK_DOVE, 0.2), innovation=0.0, n_variants=2,
           initial=(0.1, 0.9))
    r = m.simulate(60, seed=4, record=(hawk,))
    sim = r.series["<lambda>"]
    p0 = sim[0]  # recorded after the first step
    pred = theory.replicator_trajectory([0.1, 0.9], HAWK_DOVE, 0.2, 60)[1:, 0]
    assert np.max(np.abs(sim - pred)) < 0.02
    assert p0 > 0.1


def test_payoff_bias_reaches_mixed_equilibrium():
    hawk = lambda t, g: float(np.mean(t == 0))
    m = wf(1, 5000, learning=PayoffBias(HAWK_DOVE, 0.2), innovation=0.0, n_variants=2,
           initial=(0.9, 0.1))
    sim = m.simulate(200, seed=5, record=(hawk,)).series["<lambda>"]
    assert sim[100:].mean() == pytest.approx(theory.mixed_equilibrium_2x2(HAWK_DOVE), abs=0.02)


def test_coordination_game_goes_to_fixation():
    coord = ((2.0, 0.0), (0.0, 1.0))           # unstable interior point at p = 1/3
    top = lambda t, g: float(np.mean(t == 0))
    up = wf(1, 2000, learning=PayoffBias(coord, 0.4), innovation=0.0, n_variants=2,
            initial=(0.5, 0.5)).simulate(150, seed=6, record=(top,)).series["<lambda>"]
    down = wf(1, 2000, learning=PayoffBias(coord, 0.4), innovation=0.0, n_variants=2,
              initial=(0.2, 0.8)).simulate(150, seed=6, record=(top,)).series["<lambda>"]
    assert up[-1] > 0.99 and down[-1] < 0.01


def test_conformity_reduces_within_group_diversity():
    def div(theta):
        r = wf(1, 100, learning=Conformity(theta), n_models=10, innovation=0.02).simulate(
            3000, seed=7, record=("within_diversity",))
        return r.series["within_diversity"][500:].mean()
    assert div(0.8) > div(1.0) > div(2.0)
