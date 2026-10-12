import sys

import pytest

from miras import FunctionSimulator, Uniform, identify, tracked
from miras.provenance import _NullRun

import toys


def test_disabled_tracking_is_a_noop():
    with tracked("x", enabled=False) as run:
        assert isinstance(run, _NullRun)
        run.log_result("a", 1)


def test_missing_daftar_warns_and_continues(monkeypatch):
    monkeypatch.setitem(sys.modules, "daftar", None)   # makes `import daftar` fail
    with pytest.warns(UserWarning, match="daftar is not installed"):
        with tracked("x", params={"a": 1}) as run:
            run.log_result("r", 2.0)


def test_identify_records_a_daftar_run(tmp_path, monkeypatch):
    daftar = pytest.importorskip("daftar")
    store_dir = tmp_path / ".daftar"
    monkeypatch.setenv("DAFTAR_DIR", str(store_dir))   # never write into an ancestor store
    report = identify(FunctionSimulator(toys.product), {"a": Uniform(0.2, 1), "b": Uniform(0.2, 1)},
                      n_reference=400, n_test=10, seed=1, track=True, label="miras-test")
    runs = daftar.RunStore(store_dir).list(label="miras-test")
    assert len(runs) == 1
    fields = runs[0].to_dict() if hasattr(runs[0], "to_dict") else vars(runs[0])
    text = str(fields)
    assert "contraction.a" in text and "miras_version" in text
    assert report.findings
