"""The Deffner et al. (2024) workflows, ported onto the miras engine."""
import numpy as np
import pytest

from miras.paper import paper_model
from miras.paper._data import age_migration_nl


def test_packaged_data():
    m = age_migration_nl()
    assert m.shape == (91,) and 0 < m.min() and m.max() < 1


def test_paper_model_configuration():
    m = paper_model(theta=2.0, m=0.1)
    assert m.structure.N == 3000 and m.n_models == 30
    assert m.demography.max_age == 90 and m.demography.r_learn == 0.03
    assert m.learning.theta == 2.0 and not m.learning.include_self


def test_migration_erodes_diversity_under_weak_conformity():
    def fst(m):
        r = paper_model(theta=1.4, m=m, n_groups=10).simulate(60, burn_in=100, seed=3)
        return r.series["fst"][-20:].mean()
    assert fst(0.0) > fst(0.2)


def test_longitudinal_data_are_valid_stan_input():
    from miras.paper.longitudinal import DATA_PARAMS, build_stan_data, simulate_data
    P = dict(DATA_PARAMS, n_burn_in=150, n_skip=20, n_steps=8, n_record=60)
    d = simulate_data(np.random.default_rng(3), age_migration_nl(), P)
    sd = build_stan_data(d, P["n_mod"])
    f = np.array(sd["frequencies"])
    assert np.all(np.where(f < 0, 0, f).sum(1) == P["n_mod"] + 1)       # 30 models + self
    ch, inn, n_alt = map(np.array, (sd["choices"], sd["innovate"], sd["N_alt"]))
    assert np.all((ch[inn == 0] >= 1) & (ch[inn == 0] <= n_alt[inn == 0]))
    assert 0.03 < inn.mean() < 0.25                                       # true mu = 0.1
    assert sd["N"] == len(sd["age"]) and max(sd["id"]) == sd["N_id"]


def test_dags_power_analysis(tmp_path):
    pytest.importorskip("matplotlib")
    from miras.paper import dags
    dags.main(["--outdir", str(tmp_path), "--n-rep", "3", "--skip-stan"])
    assert (tmp_path / "DAGstoDataPower.pdf").exists()


def test_stan_priors_match_model_file():
    from miras.inference.stan import stan_file
    from miras.paper.longitudinal import stan_priors
    src = open(stan_file("Longitudinal_Conf")).read()
    assert "logit_mu  ~ normal(0,2)" in src and "log_theta ~ normal(0,1)" in src
    pr = stan_priors()
    assert (pr["mu"].sd, pr["theta"].sd) == (2.0, 1.0)


@pytest.mark.slow
def test_longitudinal_stan_identifiability(tmp_path):
    from miras.inference.stan import cmdstan_available
    if not cmdstan_available()[0]:
        pytest.skip("CmdStan not installed")
    from miras.paper import longitudinal
    longitudinal.main(["--quick", "--identify", "2", "--outdir", str(tmp_path), "--cores", "1"])
    assert (tmp_path / "longitudinal_identifiability.md").exists()
