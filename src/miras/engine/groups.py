"""Populations of unequal groups, with learning inside and across groups.

`GroupedPopulation` is the engine piece for models in which groups differ:
in size, in their own parameters, and in how their members pick role models
from other groups. The equal-sized `Population` used by the paper models is
left untouched, so the paper reproductions do not change.

Model choice across groups follows three ingredients that recur in cultural
evolution models:

* contact: how often a learner looks outside its own group at all;
* prestige: which other group it looks to, with probability proportional to
  size x weight (e.g. political power ** beta);
* parochial filtering: an out-group model is kept only with probability
  1 - parochialism of the learner's group; otherwise the learner falls back on
  an in-group model.
"""
from __future__ import annotations

import numpy as np


class GroupedPopulation:
    """Individuals 0..N-1 in groups of arbitrary sizes.

    Parameters
    ----------
    sizes : sequence of int
        Members per group; individuals are numbered group by group.
    rng : numpy Generator
    """

    def __init__(self, sizes, rng):
        sizes = np.asarray(sizes, dtype=int)
        if sizes.ndim != 1 or sizes.size < 1 or np.any(sizes < 1):
            raise ValueError("sizes must be a non-empty list of positive integers")
        self.rng = rng
        self.sizes = sizes
        self.n_groups = sizes.size
        self.N = int(sizes.sum())
        self.group = np.repeat(np.arange(self.n_groups), sizes)
        self.start = np.concatenate(([0], np.cumsum(sizes)[:-1]))   # first member of each group

    # ------------------------------------------------------------------ #
    def members(self, g):
        return np.arange(self.start[g], self.start[g] + self.sizes[g])

    def group_mean(self, x):
        """Mean of a per-individual quantity within each group."""
        return np.bincount(self.group, weights=np.asarray(x, float),
                           minlength=self.n_groups) / self.sizes

    def random_members(self, groups):
        """One uniformly random member of each group listed in `groups`."""
        groups = np.asarray(groups, dtype=int)
        return self.start[groups] + (self.rng.random(groups.size) * self.sizes[groups]).astype(int)

    def sample_in_group(self, focal, n):
        """(len(focal), n) random members of each focal individual's group,
        drawn with replacement (the focal individual itself can be drawn)."""
        g = self.group[np.asarray(focal, dtype=int)]
        u = self.rng.random((g.size, n))
        return self.start[g][:, None] + (u * self.sizes[g][:, None]).astype(int)

    def choose_model_groups(self, focal, contact, weights, filter_out=None):
        """Which group each focal individual takes its model from.

        contact[g]: probability a learner in g looks outside its group.
        weights[h]: attractiveness of group h as a source (size is included
        here: the probability of picking h is proportional to sizes[h] *
        weights[h], over groups other than the learner's own).
        filter_out[g]: probability a learner in g rejects an out-group model
        and falls back on its own group (parochialism).

        Returns (model_group, looked_out, kept_out) as arrays over focal."""
        focal = np.asarray(focal, dtype=int)
        g = self.group[focal]
        contact = np.broadcast_to(np.asarray(contact, float), (self.n_groups,))
        looked = self.rng.random(focal.size) < contact[g]
        src = np.where(looked, -1, g)
        pull = self.sizes * np.asarray(weights, float)
        for k in np.flatnonzero(looked):
            w = pull.copy()
            w[g[k]] = 0.0
            if w.sum() <= 0:                        # nobody else to look at
                src[k] = g[k]
                looked[k] = False
                continue
            src[k] = int(np.searchsorted(np.cumsum(w), self.rng.random() * w.sum(), side="right"))
        kept = looked.copy()
        if filter_out is not None:
            filt = np.broadcast_to(np.asarray(filter_out, float), (self.n_groups,))
            rejected = looked & (self.rng.random(focal.size) < filt[g])
            src[rejected] = g[rejected]
            kept &= ~rejected
        return src, looked, kept


def water_fill(total, caps, weights=None):
    """Share `total` among claimants in proportion to `weights`, never giving
    anyone more than their cap, and passing any excess on to the others in
    proportion to their weights (progressive filling).

    Returns the allocation x with sum(x) = min(total, sum(caps)) and
    x_i = min(cap_i, lam * w_i) for the lam that makes the total fit."""
    caps = np.asarray(caps, float)
    w = np.ones_like(caps) if weights is None else np.asarray(weights, float)
    if np.any(caps < 0) or np.any(w < 0):
        raise ValueError("caps and weights must be non-negative")
    total = float(total)
    if total >= caps.sum():
        return caps.copy()
    x = np.zeros_like(caps)
    active = (caps > 0) & (w > 0)
    remaining = total
    while remaining > 1e-12 and active.any():
        lam = remaining / w[active].sum()
        room = np.where(active, caps - x, np.inf)
        need = np.where(active, room / np.where(w > 0, w, 1), np.inf)
        step = min(lam, need[active].min())
        x[active] += step * w[active]
        remaining -= step * w[active].sum()
        full = active & (x >= caps - 1e-12)
        x[full] = caps[full]
        active &= ~full
    return x
