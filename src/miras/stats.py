"""Summary statistics of cultural variation, and study designs that decide
which individuals a study actually observes.

Every summary takes ``(traits, group)`` (0-based group labels) and returns a
float, so the same functions summarise a whole simulated population or the
sample a study would collect.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _group_freqs(traits, group):
    """(n_groups, n_variants) matrix of within-group variant frequencies."""
    _, inv = np.unique(traits, return_inverse=True)
    g_labels, g = np.unique(group, return_inverse=True)
    counts = np.zeros((g_labels.size, inv.max() + 1))
    np.add.at(counts, (g, inv), 1.0)
    return counts / counts.sum(axis=1, keepdims=True)


def cultural_fst(traits, group):
    """Cultural F_ST (Mesoudi 2018): (total - within) / total diversity.

    Returns (fst, total_diversity, between_diversity). Total diversity is
    1 - sum of squared mean frequencies; within is the mean over groups of
    1 - sum of squared group frequencies."""
    f = _group_freqs(traits, group)
    total = 1.0 - np.sum(f.mean(axis=0) ** 2)
    within = np.mean(1.0 - np.sum(f ** 2, axis=1))
    with np.errstate(invalid="ignore", divide="ignore"):
        fst = (total - within) / total if total > 0 else 0.0
    return float(fst), float(total), float(total - within)


def fst(traits, group):
    return cultural_fst(traits, group)[0]


def total_diversity(traits, group):
    return cultural_fst(traits, group)[1]


def within_diversity(traits, group):
    """Mean within-group diversity (probability two random draws differ)."""
    f = _group_freqs(traits, group)
    return float(np.mean(1.0 - np.sum(f ** 2, axis=1)))


def n_variants(traits, group):
    """Mean number of distinct variants per group."""
    return float(np.mean([np.unique(traits[group == g]).size for g in np.unique(group)]))


def total_variants(traits, group):
    """Number of distinct variants in the whole sample."""
    return float(np.unique(traits).size)


def majority_share(traits, group):
    """Mean frequency of the most common variant within groups."""
    return float(_group_freqs(traits, group).max(axis=1).mean())


SUMMARIES = {
    "fst": fst,
    "total_diversity": total_diversity,
    "within_diversity": within_diversity,
    "n_variants": n_variants,
    "total_variants": total_variants,
    "majority_share": majority_share,
}


def summarize(traits, group, names):
    unknown = [n for n in names if n not in SUMMARIES]
    if unknown:
        raise KeyError(f"unknown summaries {unknown}; available: {sorted(SUMMARIES)}")
    return np.array([SUMMARIES[n](traits, group) for n in names], dtype=float)


@dataclass(frozen=True)
class CrossSectional:
    """A cross-sectional study: observe `n_per_group` random individuals in
    each of `n_groups` random groups at the end of the simulation.
    None means everyone / every group."""

    n_groups: int | None = None
    n_per_group: int | None = None

    def sample(self, traits, group, rng):
        groups = np.unique(group)
        if self.n_groups is not None and self.n_groups < groups.size:
            groups = rng.choice(groups, self.n_groups, replace=False)
        idx = []
        for g in groups:
            members = np.flatnonzero(group == g)
            if self.n_per_group is not None and self.n_per_group < members.size:
                members = rng.choice(members, self.n_per_group, replace=False)
            idx.append(members)
        idx = np.concatenate(idx)
        return traits[idx], group[idx]
