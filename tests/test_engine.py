import numpy as np
import pytest

from miras import (AgeStructured, Conformity, Islands, Mixture, Model, Neutral, PayoffBias,
                   WrightFisher)
from miras.engine import Population
from miras.engine.learning import _pick_by_count_weight


def small(**kw):
    kw.setdefault("structure", Islands(6, 40))
    kw.setdefault("n_models", 10)
    return Model(**kw)


def test_same_seed_same_result():
    m = small(migration=0.1, learning=Conformity(1.5))
    a = m.simulate(30, burn_in=20, seed=11)
    b = m.simulate(30, burn_in=20, seed=11)
    np.testing.assert_array_equal(a.series["fst"], b.series["fst"])
    np.testing.assert_array_equal(a.population.traits, b.population.traits)


@pytest.mark.parametrize("r_dist", [0.0, 0.2])
def test_migration_preserves_group_sizes(r_dist):
    m = small(structure=Islands(6, 40, size_grid=10, r_dist=r_dist), migration=0.4)
    pop = m.new_population(np.random.default_rng(0))
    for _ in range(20):
        moved = pop.migrate(np.full(90, 0.4))
        assert np.all(np.bincount(pop.group, minlength=6) == 40)
    assert moved.size > 0


def test_migrants_leave_their_group_except_when_it_is_the_only_one_left():
    # As in the original model, the last migrants return to their own group if it
    # is the only group with free slots; that is rare, everyone else moves.
    stayed = total = 0
    for seed in range(20):
        pop = small().new_population(np.random.default_rng(seed))
        before = pop.group.copy()
        moved = pop.migrate(np.full(90, 0.3))
        stayed += int(np.sum(pop.group[moved] == before[moved]))
        total += moved.size
    assert stayed / total < 0.05


def test_models_come_from_own_group_and_are_distinct():
    pop = small().new_population(np.random.default_rng(2))
    focal = np.arange(pop.N)
    M = pop.sample_models(focal, 10)
    assert np.all(pop.group[M] == pop.group[focal][:, None])
    assert all(len(set(row)) == 10 for row in M)


def test_large_group_model_sampling_path():
    pop = Population(rng=np.random.default_rng(3), n_groups=1, group_size=100_000,
                     ages=np.ones(100_000, int))
    M = pop.sample_models(np.arange(50), 5)
    assert M.shape == (50, 5) and all(len(set(r)) == 5 for r in M)


@pytest.mark.parametrize("theta", [0.5, 1.0, 2.0, 3.0])
def test_conformity_probabilities_are_exact(theta):
    rng = np.random.default_rng(4)
    row = np.r_[np.full(15, 5), np.full(10, 6), np.full(5, 7)]
    pool = np.tile(row, (100_000, 1))
    chosen = _pick_by_count_weight(pool, theta, rng)
    c = np.array([15, 10, 5.0])
    expected = c ** theta / np.sum(c ** theta)
    observed = [np.mean(chosen == v) for v in (5, 6, 7)]
    np.testing.assert_allclose(observed, expected, atol=0.006)


def test_innovations_are_new_variants():
    m = small(innovation=1.0, demography=WrightFisher())
    r = m.simulate(1, seed=5, record=())
    assert np.unique(r.population.traits).size == r.population.N


def test_finite_variants_stay_in_range():
    m = small(innovation=0.3, n_variants=3, initial="uniform", demography=WrightFisher())
    r = m.simulate(20, seed=6, record=())
    assert set(np.unique(r.population.traits)) <= {0, 1, 2}


def test_age_structure_ages_and_births():
    m = small(demography=AgeStructured(r_mort=0.05), learning=Neutral())
    pop = m.new_population(np.random.default_rng(7))
    ages = pop.age.copy()
    babies = m.demography.step(pop)
    alive = np.setdiff1d(np.arange(pop.N), babies)
    assert babies.size > 0
    assert np.all(pop.age[babies] == 1)
    assert np.all(pop.age[alive] == ages[alive] + 1)


def test_newborns_inherit_a_parents_variant_from_their_group():
    m = small(demography=AgeStructured(r_mort=0.05))
    pop = m.new_population(np.random.default_rng(8))
    before = [set(pop.traits[pop.group == g]) for g in range(6)]
    babies = m.demography.step(pop)
    for b in babies:
        assert pop.traits[b] in before[pop.group[b]]


def test_legacy_aging_reproduces_r_quirk():
    m = small(demography=AgeStructured(r_mort=0.0, legacy_aging=True))
    pop = m.new_population(np.random.default_rng(9))
    pop.age[:] = 10
    m.demography.step(pop)          # nobody dies -> in R nobody ages
    assert np.all(pop.age == 10)


def test_age_specific_migration_vector():
    m = small(migration=[0.0] * 30 + [1.0] * 60, demography=AgeStructured())
    pop = m.new_population(np.random.default_rng(10))
    from miras.engine import migration_vector
    before = pop.group.copy()
    pop.migrate(migration_vector(m.migration, 90))
    young = pop.age <= 30
    assert np.all(pop.group[young] == before[young])


def test_set_replaces_nested_parameters():
    m = small().set({"learning.theta": 2.5, "migration": 0.2, "structure.r_dist": 0.1})
    assert m.learning.theta == 2.5 and m.migration == 0.2 and m.structure.r_dist == 0.1
    assert m.get("learning.theta") == 2.5
    with pytest.raises(AttributeError):
        small().set({"learning.nope": 1})


def test_mixture_uses_each_rule():
    rule = Mixture((Neutral(), PayoffBias(((1, 0), (0, 1)), 0.5)), (0.5, 0.5))
    m = small(learning=rule, n_variants=2, initial="uniform", demography=WrightFisher())
    r = m.simulate(10, seed=11)
    assert np.all(np.isfinite(r.series["fst"]))


def test_payoff_bias_requires_finite_variants():
    m = small(learning=PayoffBias(), demography=WrightFisher())   # infinite alleles
    with pytest.raises(ValueError, match="n_variants"):
        m.simulate(3, seed=12)


def test_n_models_cannot_exceed_group():
    with pytest.raises(ValueError):
        small(n_models=100).simulate(2, seed=1)
