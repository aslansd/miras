import numpy as np
import pytest

from miras import CrossSectional, cultural_fst, summarize


def test_fst_zero_when_groups_identical():
    traits = np.tile([0, 1, 2, 3], 5)
    group = np.repeat(np.arange(5), 4)
    fst, total, between = cultural_fst(traits, group)
    assert fst == pytest.approx(0.0) and between == pytest.approx(0.0)


def test_fst_one_when_groups_fixed_for_different_variants():
    traits = np.repeat(np.arange(5), 10)
    group = np.repeat(np.arange(5), 10)
    assert cultural_fst(traits, group)[0] == pytest.approx(1.0)


def test_fst_zero_for_monomorphic_population():
    assert cultural_fst(np.zeros(20, int), np.repeat([0, 1], 10))[0] == 0.0


def test_summaries_by_name():
    traits = np.array([0, 0, 1, 1, 1, 2])
    group = np.array([0, 0, 0, 1, 1, 1])
    s = dict(zip(["within_diversity", "n_variants", "majority_share", "total_variants"],
                 summarize(traits, group, ["within_diversity", "n_variants", "majority_share",
                                           "total_variants"])))
    assert s["n_variants"] == 2 and s["total_variants"] == 3
    assert s["majority_share"] == pytest.approx(2 / 3)
    assert s["within_diversity"] == pytest.approx(1 - (4 / 9 + 1 / 9))
    with pytest.raises(KeyError):
        summarize(traits, group, ["nonsense"])


def test_cross_sectional_design_samples():
    traits = np.arange(100)
    group = np.repeat(np.arange(10), 10)
    t, g = CrossSectional(n_groups=4, n_per_group=3).sample(traits, group, np.random.default_rng(0))
    assert len(np.unique(g)) == 4 and len(t) == 12
    assert all(np.sum(g == x) == 3 for x in np.unique(g))
