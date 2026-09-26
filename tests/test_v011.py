"""Tests for the 0.1.1 changes: convergence checks, checkpoints, lazy
matplotlib, clean interrupts."""
import subprocess
import sys
import types

import numpy as np
import pytest

from miras.inference import stan
from miras.paper import _runner


# --- convergence ------------------------------------------------------------- #
def _chains(n=1500, C=4, P=2, seed=0):
    rng = np.random.default_rng(seed)
    return rng.normal(1.1, 0.1, (n, C, P)), np.zeros((n, C))


def test_converged_fit_passes():
    draws, div = _chains()
    c = stan.assess_chains(draws, div, 1.003, names=["log_theta", "logit_mu"])
    assert c.converged and c.suspect_chains == [] and "converged" in c.report()


def test_stuck_diverging_chain_is_flagged():
    # the failure seen in the 0.1.0 end-to-end check: one chain diverging on
    # every iteration, sitting at log_theta = -1.2
    draws, div = _chains()
    draws[:, 2, 0] = -1.2
    div[:, 2] = 1
    c = stan.assess_chains(draws, div, 1.62, names=["log_theta", "logit_mu"])
    assert not c.converged and c.suspect_chains == [2] and c.divergences == 1500
    assert "chain 3 diverged on 1500 of 1500" in c.report()


def test_chain_far_from_others_is_flagged_without_divergences():
    draws, div = _chains()
    draws[:, 0, 1] += 3.0
    c = stan.assess_chains(draws, div, 1.3, names=["log_theta", "logit_mu"])
    assert c.suspect_chains == [0] and "far from the others in logit_mu" in c.report()


def test_struggling_fit_without_a_culprit():
    draws, div = _chains()
    div[:10, :] = 1
    c = stan.assess_chains(draws, div, 1.2)
    assert not c.converged and c.suspect_chains == []
    assert "whole fit is struggling" in c.report()


def test_one_divergence_means_not_converged():
    draws, div = _chains()
    div[5, 1] = 1
    assert not stan.assess_chains(draws, div, 1.001).converged


def test_cached_draws_convergence_flag_old_and_new_format():
    from miras.paper.longitudinal import draws_converged
    assert draws_converged({"_diagnostics": np.array([1.004, 0.0])})            # 0.1.0 cache
    assert not draws_converged({"_diagnostics": np.array([1.619, 1500.0])})
    assert not draws_converged({"_diagnostics": np.array([1.004, 3.0, 0.0])})   # 0.1.1 cache


def test_init_radius_reaches_cmdstan(monkeypatch):
    seen = {}

    class FakeModel:
        def __init__(self, stan_file):
            seen["file"] = stan_file

        def sample(self, **kw):
            seen.update(kw)
            return "fit"

    fake = types.SimpleNamespace(CmdStanModel=FakeModel, cmdstan_path=lambda: "/x")
    monkeypatch.setitem(sys.modules, "cmdstanpy", fake)
    monkeypatch.setattr(stan, "_compilable_copy", lambda name: f"/cache/{name}.stan")
    assert stan.sample("dags_to_data", {}, init_radius=0.5) == "fit"
    assert seen["inits"] == 0.5
    seen.clear()
    stan.sample("dags_to_data", {})
    assert "inits" not in seen                      # default: Stan's own


def test_missing_cmdstan_message_is_actionable(monkeypatch):
    def boom():
        raise ValueError("no cmdstan")
    monkeypatch.setitem(sys.modules, "cmdstanpy", types.SimpleNamespace(cmdstan_path=boom))
    ok, msg = stan.cmdstan_available()
    assert not ok and "install_cmdstan" in msg and "CERTIFICATE_VERIFY_FAILED" in msg
    assert "python -m cmdstanpy" not in msg


# --- checkpoints and progress ------------------------------------------------ #
def test_checkpoint_roundtrip_and_key_mismatch(tmp_path):
    path = tmp_path / "c.npz"
    ck = _runner.Checkpoint(path, {"a": 1})
    assert ck.load() is None
    ck.save(x=np.arange(3), done=np.array([True, False, True]))
    back = _runner.Checkpoint(path, {"a": 1}).load()
    np.testing.assert_array_equal(back["x"], [0, 1, 2])
    assert _runner.Checkpoint(path, {"a": 2}).load() is None     # different settings: ignored
    ck.remove()
    assert not path.exists()


def test_corrupt_checkpoint_is_ignored(tmp_path):
    path = tmp_path / "c.npz"
    path.write_bytes(b"not a checkpoint")
    assert _runner.Checkpoint(path, {"a": 1}).load() is None


def test_progress_prints_time_left(capsys):
    p = _runner.Progress(10, every=5)
    for _ in range(5):
        p.tick()
    assert "5/10" in capsys.readouterr().out
    assert _runner.fmt_duration(30) == "30s" and _runner.fmt_duration(7 * 3600 + 25 * 60) == "7h 25m"


def test_abm_sweep_resumes_to_identical_results(tmp_path, monkeypatch):
    from miras.paper import abm
    # a small sweep: the first four combinations (same values in spawned workers)
    monkeypatch.setattr(abm, "SWEEP_THETA", abm.SWEEP_THETA[:4])
    monkeypatch.setattr(abm, "SWEEP_M", abm.SWEEP_M[:4])
    full = abm.run_sweep(2, 5, 1, 7, 5, False)
    # pretend an interrupted run finished every other simulation
    done = np.zeros(8, bool)
    done[::2] = True
    partial = np.full_like(full, np.nan)
    for k in np.flatnonzero(done):
        partial[k // 2, k % 2] = full[k // 2, k % 2]
    ck = _runner.Checkpoint(tmp_path / "abm.npz", {"t": 1})
    ck.save(fst=partial, done=done)
    resumed = abm.run_sweep(2, 5, 1, 7, 5, False, checkpoint=ck)
    np.testing.assert_array_equal(resumed, full)
    assert not (tmp_path / "abm.npz").exists()           # removed once complete


def test_interrupt_exits_cleanly(monkeypatch, capsys):
    from miras import cli
    from miras.paper import dags

    def interrupted(argv):
        raise KeyboardInterrupt
    monkeypatch.setattr(dags, "main", interrupted)
    assert cli.main(["paper", "dags"]) == 130
    assert "Interrupted." in capsys.readouterr().err


# --- packaging ---------------------------------------------------------------- #
def test_paper_modules_import_without_matplotlib():
    code = ("import sys; sys.modules['matplotlib'] = None; "
            "import miras.paper.longitudinal, miras.paper.dags, miras.paper.abm; print('ok')")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert out.stdout.strip() == "ok", out.stderr


def test_report_notes_are_shown():
    from miras import Uniform, analyze
    from miras.inference.abc import Posterior
    pri = {"a": Uniform(0, 1)}
    rng = np.random.default_rng(0)
    truths = rng.uniform(0, 1, (5, 1))
    posts = [Posterior(pri, rng.normal(t, 0.01, (200, 1)), np.ones(200)) for t in truths]
    rep = analyze(pri, truths, posts, info={"notes": ["2 of 7 Stan fits did not converge"]})
    assert "note: 2 of 7 Stan fits" in rep.summary()
    assert "## Notes" in rep.to_markdown()
