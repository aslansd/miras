"""Simulators: parameters -> summary statistics.

A simulator is any callable ``sim(params: dict, seed: int) -> 1-d array`` with
a ``summary_names`` attribute. `ModelSimulator` builds one from a miras
`Model`, a study design and a list of summaries; `FunctionSimulator` wraps an
arbitrary function (useful for toy problems and external models).
"""
from __future__ import annotations

import os
from multiprocessing import get_context

import numpy as np

from ..stats import CrossSectional


class ModelSimulator:
    """Simulate a `Model` with the given parameters and summarise the data a
    study with `design` would collect at the end of the run.

    Parameters are addressed by dotted names, e.g. ``"learning.theta"``,
    ``"migration"``, ``"innovation"``."""

    def __init__(self, model, summaries=("fst",), design=None, n_steps=200, burn_in=0):
        self.model = model
        self.summary_names = tuple(summaries)
        self.design = design if design is not None else CrossSectional()
        self.n_steps = int(n_steps)
        self.burn_in = int(burn_in)

    def __call__(self, params: dict, seed: int) -> np.ndarray:
        rng = np.random.default_rng(seed)
        result = self.model.set(params).simulate(self.n_steps, burn_in=self.burn_in,
                                                 rng=rng, record=())
        return result.summaries(self.summary_names, self.design, rng)

    def describe(self) -> dict:
        return {"model": repr(self.model), "summaries": list(self.summary_names),
                "design": repr(self.design), "n_steps": self.n_steps, "burn_in": self.burn_in}


class FunctionSimulator:
    """Wrap ``fn(params: dict, rng) -> array-like``. For cores > 1 `fn` must be
    picklable (defined at module top level, not a lambda)."""

    def __init__(self, fn, summary_names=None):
        self.fn = fn
        self.summary_names = tuple(summary_names) if summary_names else None

    def __call__(self, params: dict, seed: int) -> np.ndarray:
        return np.atleast_1d(np.asarray(self.fn(params, np.random.default_rng(seed)), float))

    def describe(self) -> dict:
        return {"function": getattr(self.fn, "__qualname__", repr(self.fn))}


def as_simulator(sim):
    if isinstance(sim, (ModelSimulator, FunctionSimulator)) or hasattr(sim, "summary_names"):
        return sim
    if callable(sim):
        return FunctionSimulator(sim)
    raise TypeError("simulator must be a ModelSimulator or a callable(params, rng)")


def _call(args):
    sim, params, seed = args
    try:
        return sim(params, seed)
    except Exception as exc:  # a failed simulation must not kill a long run
        return exc


def run_batch(sim, param_dicts, seeds, cores=1, chunksize=None):
    """Evaluate the simulator for many parameter sets. Returns an (n, s) array;
    rows of failed simulations are NaN (with a warning)."""
    tasks = [(sim, p, int(s)) for p, s in zip(param_dicts, seeds)]
    if cores is None:
        cores = os.cpu_count() or 1
    if cores > 1 and len(tasks) > 1:
        chunksize = chunksize or max(1, len(tasks) // (4 * cores))
        with get_context("spawn" if os.name == "nt" else "fork").Pool(cores) as pool:
            out = pool.map(_call, tasks, chunksize=chunksize)
    else:
        out = [_call(t) for t in tasks]
    n_fail = sum(isinstance(o, Exception) for o in out)
    width = next((len(o) for o in out if not isinstance(o, Exception)), 1)
    if n_fail:
        import warnings
        first = next(o for o in out if isinstance(o, Exception))
        warnings.warn(f"{n_fail}/{len(out)} simulations failed; first error: {first!r}")
    return np.array([np.full(width, np.nan) if isinstance(o, Exception) else o for o in out])


def seeds_for(seed, n):
    """n independent integer seeds derived from one seed."""
    return np.random.SeedSequence(seed).generate_state(n, dtype=np.uint64) % (2**63)
