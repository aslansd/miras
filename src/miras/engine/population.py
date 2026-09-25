"""Population state and the primitive operations the model is built from.

Indexing: individuals and groups are 0-based. Ages are 1-based (1 = newborn),
so an age-specific migration vector `m` is read as ``m[age - 1]``.
"""
from __future__ import annotations

import numpy as np


def migration_vector(m, max_age: int) -> np.ndarray:
    """Scalar or age-specific migration probabilities as a vector indexed by
    age-1. Ages beyond a supplied vector get probability 0. Clipped to [0, 1]."""
    m = np.atleast_1d(np.asarray(m, dtype=float))
    if m.size == 1:
        out = np.full(max(max_age, 1), m[0])
    else:
        out = np.zeros(max(max_age, m.size))
        out[: m.size] = m
    return np.clip(out, 0.0, 1.0)


class Population:
    def __init__(self, *, rng, n_groups, group_size, ages, dist=None, r_dist=0.0,
                 n_variants=None, initial="unique_per_group"):
        self.rng = rng
        self.n_groups = int(n_groups)
        self.group_size = int(group_size)
        self.N = self.n_groups * self.group_size
        self.n_variants = n_variants
        self.age = np.asarray(ages, dtype=np.int64)
        self.group = np.repeat(np.arange(self.n_groups), self.group_size)
        self.dist = np.zeros((self.n_groups,) * 2) if dist is None else dist
        self._mig_w = np.exp(-r_dist * self.dist).tolist()
        self._uniform_mig = r_dist == 0

        if isinstance(initial, str) and initial == "unique_per_group":
            if n_variants is not None and n_variants < self.n_groups:
                labels = rng.integers(0, n_variants, self.n_groups)
            else:
                labels = rng.permutation(self.n_groups)
            self.traits = labels[self.group].astype(np.int64)
        elif isinstance(initial, str) and initial == "monomorphic":
            self.traits = np.zeros(self.N, dtype=np.int64)
        elif isinstance(initial, str) and initial == "uniform":
            if n_variants is None:
                raise ValueError("initial='uniform' needs n_variants")
            self.traits = rng.integers(0, n_variants, self.N).astype(np.int64)
        else:                                               # explicit frequencies
            p = np.asarray(initial, float)
            p = p / p.sum()
            self.traits = rng.choice(p.size, size=self.N, p=p).astype(np.int64)
        self.counter = int(self.traits.max())               # last variant id used

    # ---------------------------------------------------------------- #
    def migrate(self, m_by_age: np.ndarray) -> np.ndarray:
        """Each individual migrates with its age-specific probability. Migrants
        are processed in random order; each picks a group other than its own
        among those with free slots (distance-weighted). Group sizes are kept.
        As in the original model, when only one group still has free slots the
        remaining migrants go there, even if it is their own."""
        rng = self.rng
        a = np.minimum(self.age, m_by_age.size) - 1
        p = np.where(self.age > m_by_age.size, 0.0, m_by_age[a])
        migrants = rng.permutation(np.flatnonzero(rng.random(self.N) < p))
        if migrants.size == 0 or self.n_groups == 1:
            return migrants[:0]
        G = self.n_groups
        spots = np.bincount(self.group[migrants], minlength=G).tolist()
        n_open = sum(1 for s in spots if s > 0)
        u = rng.random(migrants.size).tolist()
        new_group = []
        for k, gi in enumerate(self.group[migrants].tolist()):
            if n_open == 1:
                new = next(g for g in range(G) if spots[g] > 0)
            else:
                cand = [g for g in range(G) if spots[g] > 0 and g != gi]
                if self._uniform_mig:
                    new = cand[int(u[k] * len(cand))]
                else:
                    w = [self._mig_w[gi][g] for g in cand]
                    target, acc, new = u[k] * sum(w), 0.0, cand[-1]
                    for g, wg in zip(cand, w):
                        acc += wg
                        if target < acc:
                            new = g
                            break
            new_group.append(new)
            spots[new] -= 1
            if spots[new] == 0:
                n_open -= 1
        self.group[migrants] = new_group
        return migrants

    def members(self) -> np.ndarray:
        """(n_groups, group_size) matrix of individuals in each group."""
        return np.argsort(self.group, kind="stable").reshape(self.n_groups, self.group_size)

    def sample_models(self, focal: np.ndarray, n_models: int) -> np.ndarray:
        """For each focal individual, `n_models` distinct role models drawn
        uniformly from its current group (the focal individual can be drawn,
        as in the original model)."""
        k, gs = int(n_models), self.group_size
        if k > gs:
            raise ValueError("n_models cannot exceed group_size")
        members = self.members()
        rng = self.rng
        if gs <= 4 * k or focal.size * gs <= 2_000_000:
            keys = rng.random((focal.size, gs))
            pick = np.argpartition(keys, k - 1, axis=1)[:, :k] if k < gs else np.argsort(keys, 1)
        else:                         # large groups: sample indices, redraw rows with repeats
            pick = rng.integers(0, gs, (focal.size, k))
            while k > 1:
                s = np.sort(pick, axis=1)
                bad = np.flatnonzero((s[:, 1:] == s[:, :-1]).any(axis=1))
                if bad.size == 0:
                    break
                pick[bad] = rng.integers(0, gs, (bad.size, k))
        return members[self.group[focal][:, None], pick]

    def update(self, learners: np.ndarray, new: np.ndarray, innovation: float):
        """Set learners' variants, replacing a fraction `innovation` by
        innovations: brand-new variants (infinite-alleles) or, with a finite
        set of variants, a uniformly random variant."""
        if learners.size == 0:
            return
        new = np.asarray(new, dtype=np.int64).copy()
        innov = self.rng.random(learners.size) < innovation
        n = int(innov.sum())
        if n:
            if self.n_variants is None:
                new[innov] = self.counter + np.arange(1, n + 1)
                self.counter += n
            else:
                new[innov] = self.rng.integers(0, self.n_variants, n)
        self.traits[learners] = new
