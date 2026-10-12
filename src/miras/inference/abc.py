"""Approximate Bayesian Computation.

Two backends:

* `ReferenceTable` -- simulate once from the prior, then answer any number of
  posterior queries by rejection (nearest simulations), optionally with
  local-linear regression adjustment (Beaumont, Zhang & Balding 2002). The
  table is amortised: the identifiability report queries it for many
  pseudo-observed datasets at the cost of one set of simulations. This is
  the approach of the original ABC analysis in Deffner et al. (2024).
* `ABCSMC` -- sequential Monte Carlo ABC (population Monte Carlo,
  Beaumont et al. 2009) with adaptive tolerances. More simulations per
  dataset, but much sharper posteriors for one observed dataset.

Distances are Euclidean on summaries scaled by their median absolute
deviation under the prior predictive distribution.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .priors import as_priors
from .simulators import as_simulator, run_batch, seeds_for


def mad_scale(S):
    """Median absolute deviation per column, falling back to the SD (or 1)."""
    S = np.asarray(S, float)
    mad = 1.4826 * np.nanmedian(np.abs(S - np.nanmedian(S, axis=0)), axis=0)
    sd = np.nanstd(S, axis=0)
    return np.where(mad > 0, mad, np.where(sd > 0, sd, 1.0))


@dataclass
class Posterior:
    """Weighted posterior samples on the working (u) scale."""

    priors: object
    U: np.ndarray
    weights: np.ndarray
    info: dict = field(default_factory=dict)

    def __post_init__(self):
        self.priors = as_priors(self.priors)
        w = np.asarray(self.weights, float)
        self.weights = w / w.sum()

    @property
    def names(self): return self.priors.names

    @property
    def samples(self) -> dict:
        """Samples on the natural scale (use with `weights`)."""
        X = self.priors.to_x(self.U)
        return {n: X[:, j] for j, n in enumerate(self.names)}

    def mean(self) -> dict:
        X = self.priors.to_x(self.U)
        return self.priors.as_dict(self.weights @ X)

    def cov_u(self) -> np.ndarray:
        mu = self.weights @ self.U
        D = self.U - mu
        return (D * self.weights[:, None]).T @ D / max(1e-12, 1 - np.sum(self.weights ** 2))

    def quantiles(self, q) -> dict:
        X = self.priors.to_x(self.U)
        out = {}
        for j, n in enumerate(self.names):
            o = np.argsort(X[:, j])
            cw = np.cumsum(self.weights[o])
            out[n] = np.interp(q, cw - self.weights[o] / 2, X[o, j])
        return out

    def resample(self, n, rng=None) -> dict:
        rng = rng or np.random.default_rng()
        idx = rng.choice(len(self.weights), n, p=self.weights)
        X = self.priors.to_x(self.U[idx])
        return {k: X[:, j] for j, k in enumerate(self.names)}


class ReferenceTable:
    """Parameters drawn from the prior with their simulated summaries."""

    def __init__(self, priors, U, S, summary_names=None, info=None):
        self.priors = as_priors(priors)
        ok = np.all(np.isfinite(S), axis=1)
        self.U, self.S = np.asarray(U)[ok], np.asarray(S, float)[ok]
        self.summary_names = summary_names
        self.scale = mad_scale(self.S)
        self.info = info or {}
        self.info["n_dropped"] = int((~ok).sum())

    @classmethod
    def build(cls, simulator, priors, n, *, seed=0, cores=1):
        sim = as_simulator(simulator)
        priors = as_priors(priors)
        rng = np.random.default_rng(seed)
        U = priors.sample_u(rng, n)
        X = priors.to_x(U)
        S = run_batch(sim, [priors.as_dict(x) for x in X], seeds_for(seed + 1, n), cores)
        return cls(priors, U, S, getattr(sim, "summary_names", None), {"n_simulations": n})

    def __len__(self): return len(self.U)

    def select(self, summaries) -> "ReferenceTable":
        """A table restricted to some summaries. Comparing designs that differ
        only in which summaries they measure then needs no new simulations."""
        names = list(self.summary_names or [])
        cols = [names.index(s) for s in summaries]
        t = ReferenceTable(self.priors, self.U, self.S[:, cols], list(summaries), dict(self.info))
        return t

    def save(self, path):
        np.savez_compressed(path, U=self.U, S=self.S, names=np.array(self.summary_names or []),
                            prior_names=np.array(self.priors.names))

    @classmethod
    def load(cls, path, priors):
        z = np.load(path, allow_pickle=False)
        pr = as_priors(priors)
        if list(z["prior_names"]) != pr.names:
            raise ValueError("saved table was built for different parameters")
        return cls(pr, z["U"], z["S"], [str(n) for n in z["names"]] or None)

    def posterior(self, observed, *, accept=0.05, adjust=True, exclude=None) -> Posterior:
        """Rejection ABC: keep the closest `accept` fraction (or count, if >= 1)
        of the table. `exclude` drops rows (e.g. the pseudo-observed row
        itself during cross-validation)."""
        obs = np.asarray(observed, float)
        d = np.sqrt((((self.S - obs) / self.scale) ** 2).sum(axis=1))
        if exclude is not None:
            d = d.copy()
            d[np.atleast_1d(exclude)] = np.inf
        n_avail = int(np.isfinite(d).sum())
        k = int(accept) if accept >= 1 else max(10, int(round(accept * n_avail)))
        k = min(k, n_avail)
        idx = np.argpartition(d, k - 1)[:k]
        eps = d[idx].max() * (1 + 1e-9) or 1e-12
        kern = 1.0 - (d[idx] / eps) ** 2                       # Epanechnikov
        U = self.U[idx]
        X = (self.S[idx] - obs) / self.scale
        if adjust and k > 3 * (X.shape[1] + 1):
            W = self.priors.u_to_w(U)
            A = np.column_stack([np.ones(k), X])
            sw = np.sqrt(kern)
            beta, *_ = np.linalg.lstsq(A * sw[:, None], W * sw[:, None], rcond=None)
            U = self.priors.w_to_u(W - X @ beta[1:])
        return Posterior(self.priors, U, np.maximum(kern, 1e-12),
                         {"method": "rejection", "k": k, "epsilon": float(eps), "adjusted": adjust})


class ABCSMC:
    """Sequential Monte Carlo ABC with adaptive tolerances.

    Generation 0 simulates n_particles / quantile draws from the prior and keeps
    the closest n_particles. Each later generation sets the tolerance to the
    `quantile` of the current particles' distances, proposes by resampling and
    perturbing particles on the unbounded w scale (Gaussian kernel with twice the
    weighted covariance), and reweights by prior / proposal density. Stops after
    `n_generations` or when the acceptance rate falls below `min_acceptance`.
    """

    def __init__(self, simulator, priors, *, n_particles=300, n_generations=6,
                 quantile=0.5, min_acceptance=0.02, batch=None, cores=1, scale=None):
        self.sim = as_simulator(simulator)
        self.priors = as_priors(priors)
        self.n = int(n_particles)
        self.G = int(n_generations)
        self.q = float(quantile)
        self.min_acc = float(min_acceptance)
        self.batch = batch or self.n
        self.cores = cores
        self.scale = scale

    def _simulate(self, U, seed):
        X = self.priors.to_x(U)
        return run_batch(self.sim, [self.priors.as_dict(x) for x in X],
                         seeds_for(seed, len(U)), self.cores)

    def run(self, observed, *, seed=0) -> Posterior:
        rng = np.random.default_rng(seed)
        obs = np.asarray(observed, float)
        pr = self.priors
        n_sims = 0

        # generation 0: prior
        n0 = int(np.ceil(self.n / self.q))
        U = pr.sample_u(rng, n0)
        S = self._simulate(U, rng.integers(2**62))
        n_sims += n0
        ok = np.all(np.isfinite(S), 1)
        U, S = U[ok], S[ok]
        scale = self.scale if self.scale is not None else mad_scale(S)
        dist = lambda S_: np.sqrt((((S_ - obs) / scale) ** 2).sum(axis=1))
        d = dist(S)
        keep = np.argsort(d)[: self.n]
        U, d = U[keep], d[keep]
        wts = np.full(len(U), 1.0 / len(U))
        eps_hist = [float(d.max())]
        acc_hist = [len(U) / n0]

        for _ in range(1, self.G):
            eps = float(np.quantile(d, self.q))
            W = pr.u_to_w(U)
            mu = wts @ W
            cov = 2.0 * ((W - mu) * wts[:, None]).T @ (W - mu) / max(1e-12, 1 - np.sum(wts ** 2))
            cov += 1e-10 * np.eye(len(mu))
            L = np.linalg.cholesky(cov)
            inv = np.linalg.inv(cov)
            logdet = 2 * np.log(np.diag(L)).sum()
            new_W, new_d, tried = [], [], 0
            while len(new_W) < self.n:
                parents = rng.choice(len(W), self.batch, p=wts)
                Wp = W[parents] + rng.standard_normal((self.batch, len(mu))) @ L.T
                Sp = self._simulate(pr.w_to_u(Wp), rng.integers(2**62))
                tried += self.batch
                dp = dist(Sp)
                hit = np.isfinite(dp) & (dp <= eps)
                new_W.extend(Wp[hit])
                new_d.extend(dp[hit])
                if tried >= self.n / self.min_acc:
                    break
            n_sims += tried
            acc = len(new_W) / tried
            if len(new_W) < max(10, self.n // 5):
                break                                           # too few accepted: stop
            Wn = np.array(new_W[: self.n])
            dn = np.array(new_d[: self.n])
            # weights: prior(w) / sum_j wts_j K(w | W_j)
            diff = Wn[:, None, :] - W[None, :, :]
            m2 = np.einsum("abi,ij,abj->ab", diff, inv, diff)
            logK = -0.5 * m2 - 0.5 * logdet
            logmix = np.log(np.exp(logK - logK.max(1, keepdims=True)) @ wts) + logK.max(1)
            logw = pr.logpdf_w(Wn) - logmix
            wn = np.exp(logw - logw.max())
            U, d, wts = pr.w_to_u(Wn), dn, wn / wn.sum()
            eps_hist.append(eps)
            acc_hist.append(acc)
            if acc < self.min_acc:
                break

        return Posterior(pr, U, wts, {"method": "abc-smc", "epsilons": eps_hist,
                                      "acceptance": acc_hist, "n_simulations": n_sims})
