"""Provenance through daftar (https://pypi.org/project/daftar/).

An identifiability report is an experiment: it depends on seeds, priors,
summaries, library versions and the simulator. With daftar installed,
``identify(..., track=True)`` and ``miras paper ... --track`` record all of that,
so two reports can be diffed with ``daftar diff`` instead of eyeballed.

Without daftar everything behaves identically and nothing is recorded: the
integration is a no-op, not an error.
"""
from __future__ import annotations

import contextlib
import warnings


def daftar_available() -> bool:
    try:
        import daftar  # noqa: F401
        return True
    except ImportError:
        return False


class _NullRun:
    """Stand-in for daftar.Run when tracking is off or daftar is missing."""

    id = None

    def log_param(self, *a, **k): pass
    def log_params(self, *a, **k): pass
    def log_result(self, *a, **k): pass
    def log_results(self, *a, **k): pass
    def add_input(self, *a, **k): pass
    def add_output(self, *a, **k): pass
    def note(self, *a, **k): pass


@contextlib.contextmanager
def tracked(label: str, *, params: dict | None = None, seed: int | None = None,
            enabled: bool = True, **kwargs):
    """``with tracked("label", params=..., seed=...) as run: run.log_result(...)``

    Yields a daftar Run when `enabled` and daftar is installed, otherwise an
    object with the same methods that records nothing."""
    if not enabled:
        yield _NullRun()
        return
    try:
        import daftar
    except ImportError:
        warnings.warn("track=True but daftar is not installed (pip install daftar); "
                      "continuing without provenance.", stacklevel=3)
        yield _NullRun()
        return
    from . import __version__
    p = {"miras_version": __version__, **(params or {})}
    p = {k: (v if isinstance(v, (int, float, str, bool)) or v is None else repr(v)) for k, v in p.items()}
    with daftar.track(label, params=p, seed=seed, tags=["miras"], **kwargs) as run:
        yield run
