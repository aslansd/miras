"""Priors over model parameters.

Each prior has two scales besides the natural one (x):

* ``u`` -- the working scale. Uniform: u = x. LogUniform: u = log x.
  Normal(transform=...): u = x, log x or logit x. The prior is uniform or
  normal on u, and identifiability is measured on u (posterior variance
  relative to prior variance).
* ``w`` -- an unbounded version of u used for regression adjustment and SMC
  proposals, so that adjusted samples never leave the prior support.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _logit(p):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return np.log(p) - np.log1p(-p)


def _expit(x):
    return 1.0 / (1.0 + np.exp(-x))


class Prior:
    def sample_u(self, rng, n): ...
    def to_u(self, x): ...
    def from_u(self, u): ...
    def u_to_w(self, u): return u
    def w_to_u(self, w): return w
    def in_support_u(self, u): return np.isfinite(u)
    def log_du_dw(self, w): return np.zeros_like(np.asarray(w, float))
    def logpdf_u(self, u): ...
    mean_u: float
    sd_u: float

    def sample(self, rng, n):
        return self.from_u(self.sample_u(rng, n))


@dataclass(frozen=True)
class Uniform(Prior):
    low: float
    high: float

    def __post_init__(self):
        if not self.high > self.low:
            raise ValueError("Uniform needs high > low")

    def sample_u(self, rng, n): return rng.uniform(self.low, self.high, n)
    def to_u(self, x): return np.asarray(x, float)
    def from_u(self, u): return np.asarray(u, float)
    def u_to_w(self, u): return _logit((np.asarray(u) - self.low) / (self.high - self.low))
    def w_to_u(self, w): return self.low + (self.high - self.low) * _expit(np.asarray(w))
    def in_support_u(self, u): return (u >= self.low) & (u <= self.high)
    def log_du_dw(self, w):
        e = _expit(np.asarray(w, float))
        return np.log(self.high - self.low) + np.log(np.clip(e * (1 - e), 1e-300, None))
    def logpdf_u(self, u):
        return np.where(self.in_support_u(u), -np.log(self.high - self.low), -np.inf)

    @property
    def mean_u(self): return 0.5 * (self.low + self.high)
    @property
    def sd_u(self): return (self.high - self.low) / np.sqrt(12.0)


@dataclass(frozen=True)
class LogUniform(Prior):
    """Uniform on log x, for scale-like parameters spanning orders of magnitude."""
    low: float
    high: float

    def __post_init__(self):
        if not self.high > self.low > 0:
            raise ValueError("LogUniform needs high > low > 0")

    @property
    def _u(self): return Uniform(np.log(self.low), np.log(self.high))
    def sample_u(self, rng, n): return self._u.sample_u(rng, n)
    def to_u(self, x): return np.log(np.asarray(x, float))
    def from_u(self, u): return np.exp(np.asarray(u, float))
    def u_to_w(self, u): return self._u.u_to_w(u)
    def w_to_u(self, w): return self._u.w_to_u(w)
    def in_support_u(self, u): return self._u.in_support_u(u)
    def log_du_dw(self, w): return self._u.log_du_dw(w)
    def logpdf_u(self, u): return self._u.logpdf_u(u)
    @property
    def mean_u(self): return self._u.mean_u
    @property
    def sd_u(self): return self._u.sd_u


@dataclass(frozen=True)
class Normal(Prior):
    """Normal on the working scale u, where x = u, exp(u) or expit(u)
    (transform None, 'log' or 'logit'). E.g. the Stan model's
    ``log_theta ~ normal(0, 1)`` is ``Normal(0, 1, transform='log')``."""
    mean: float = 0.0
    sd: float = 1.0
    transform: str | None = None

    def sample_u(self, rng, n): return rng.normal(self.mean, self.sd, n)

    def to_u(self, x):
        x = np.asarray(x, float)
        return {None: lambda v: v, "log": np.log, "logit": _logit}[self.transform](x)

    def from_u(self, u):
        u = np.asarray(u, float)
        return {None: lambda v: v, "log": np.exp, "logit": _expit}[self.transform](u)

    def logpdf_u(self, u):
        z = (np.asarray(u) - self.mean) / self.sd
        return -0.5 * z ** 2 - np.log(self.sd * np.sqrt(2 * np.pi))

    @property
    def mean_u(self): return self.mean
    @property
    def sd_u(self): return self.sd


class Priors:
    """An ordered collection of independent priors keyed by parameter name."""

    def __init__(self, priors: dict):
        if not priors:
            raise ValueError("need at least one prior")
        self.names = list(priors)
        self.priors = [priors[n] for n in self.names]

    def __len__(self): return len(self.names)

    def sample_u(self, rng, n):
        return np.column_stack([p.sample_u(rng, n) for p in self.priors])

    def to_x(self, U):
        U = np.atleast_2d(U)
        return np.column_stack([p.from_u(U[:, j]) for j, p in enumerate(self.priors)])

    def to_u(self, X):
        X = np.atleast_2d(X)
        return np.column_stack([p.to_u(X[:, j]) for j, p in enumerate(self.priors)])

    def u_to_w(self, U):
        return np.column_stack([p.u_to_w(U[:, j]) for j, p in enumerate(self.priors)])

    def w_to_u(self, W):
        return np.column_stack([p.w_to_u(W[:, j]) for j, p in enumerate(self.priors)])

    def in_support(self, U):
        return np.all(np.column_stack([p.in_support_u(U[:, j]) for j, p in enumerate(self.priors)]), 1)

    def logpdf_w(self, W):
        """Prior log density on the w scale (includes the Jacobian du/dw)."""
        U = self.w_to_u(W)
        return self.logpdf(U) + np.sum(np.column_stack(
            [p.log_du_dw(W[:, j]) for j, p in enumerate(self.priors)]), 1)

    def logpdf(self, U):
        return np.sum(np.column_stack([p.logpdf_u(U[:, j]) for j, p in enumerate(self.priors)]), 1)

    @property
    def mean_u(self): return np.array([p.mean_u for p in self.priors])

    @property
    def sd_u(self): return np.array([p.sd_u for p in self.priors])

    def as_dict(self, x_row):
        return {n: float(v) for n, v in zip(self.names, x_row)}


def as_priors(priors) -> Priors:
    return priors if isinstance(priors, Priors) else Priors(dict(priors))
