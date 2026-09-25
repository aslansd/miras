import numpy as np
import pytest

from miras import (ABCSMC, Conformity, FunctionSimulator, Islands, LogUniform, Model,
                   ModelSimulator, Normal, ReferenceTable, Uniform, WrightFisher)
from miras.inference.priors import Priors
from miras.inference.simulators import run_batch

import toys


@pytest.mark.parametrize("prior", [Uniform(0.2, 3), LogUniform(0.01, 10),
                                   Normal(0, 2, "logit"), Normal(1, 0.5, "log"), Normal(3, 1)])
def test_prior_transforms_roundtrip(prior):
    rng = np.random.default_rng(0)
    u = prior.sample_u(rng, 1000)
    np.testing.assert_allclose(prior.to_u(prior.from_u(u)), u, rtol=1e-9, atol=1e-9)
    np.testing.assert_allclose(prior.w_to_u(prior.u_to_w(u)), u, rtol=1e-7, atol=1e-7)
    assert abs(u.mean() - prior.mean_u) < 4 * prior.sd_u / np.sqrt(1000)
    assert u.std() == pytest.approx(prior.sd_u, rel=0.1)


def test_reference_table_recovers_normal_mean():
    sim = FunctionSimulator(toys.normal_mean)
    table = ReferenceTable.build(sim, {"mu": Uniform(-5, 5)}, 20000, seed=1)
    post = table.posterior([1.3, 0.0], accept=0.02, adjust=True)
    assert post.mean()["mu"] == pytest.approx(1.3, abs=0.05)
    assert np.sqrt(post.cov_u()[0, 0]) == pytest.approx(0.2, rel=0.2)   # analytic: 1/sqrt(25)


def test_regression_adjustment_sharpens_and_stays_in_support():
    table = ReferenceTable.build(FunctionSimulator(toys.normal_mean), {"mu": Uniform(1, 5)},
                                 5000, seed=2)
    raw = table.posterior([1.05, 0.0], accept=0.05, adjust=False)
    adj = table.posterior([1.05, 0.0], accept=0.05, adjust=True)
    assert adj.cov_u()[0, 0] < raw.cov_u()[0, 0]
    assert adj.samples["mu"].min() >= 1.0


def test_abc_smc_recovers_normal_mean():
    post = ABCSMC(FunctionSimulator(toys.normal_mean), {"mu": Uniform(-5, 5)},
                  n_particles=300, n_generations=6).run([1.3, 0.0], seed=3)
    assert post.mean()["mu"] == pytest.approx(1.3, abs=0.1)
    assert post.info["epsilons"] == sorted(post.info["epsilons"], reverse=True)


def test_model_simulator_and_parallel_batch_agree():
    m = Model(structure=Islands(4, 20), demography=WrightFisher(), learning=Conformity(),
              n_models=5, innovation=0.05)
    sim = ModelSimulator(m, summaries=("fst", "n_variants"), n_steps=20)
    params = [{"learning.theta": 1.5, "migration": 0.1}] * 3
    serial = run_batch(sim, params, [1, 2, 3], cores=1)
    parallel = run_batch(sim, params, [1, 2, 3], cores=2)
    np.testing.assert_array_equal(serial, parallel)
    assert serial.shape == (3, 2)


def _fails(p, r):
    if p["a"] > 0.5:
        raise RuntimeError("boom")
    return [p["a"]]


def test_failed_simulations_become_nan_and_are_dropped():
    with pytest.warns(UserWarning, match="failed"):
        table = ReferenceTable.build(FunctionSimulator(_fails), {"a": Uniform(0, 1)}, 200, seed=4)
    assert 0 < len(table) < 200 and table.info["n_dropped"] > 0


def test_table_select_and_save_load(tmp_path):
    table = ReferenceTable.build(FunctionSimulator(toys.identified, ["x", "y"]),
                                 {"a": Uniform(0, 1), "b": Uniform(0, 1)}, 300, seed=5)
    sub = table.select(["y"])
    assert sub.S.shape == (len(table), 1) and sub.summary_names == ["y"]
    path = tmp_path / "t.npz"
    table.save(path)
    back = ReferenceTable.load(path, {"a": Uniform(0, 1), "b": Uniform(0, 1)})
    np.testing.assert_array_equal(back.S, table.S)
    with pytest.raises(ValueError):
        ReferenceTable.load(path, {"a": Uniform(0, 1)})


def test_priors_collection():
    pr = Priors({"x": Uniform(0, 1), "y": LogUniform(1, 100)})
    U = pr.sample_u(np.random.default_rng(6), 50)
    assert pr.in_support(U).all()
    X = pr.to_x(U)
    assert (X[:, 1] >= 1).all() and (X[:, 1] <= 100).all()
