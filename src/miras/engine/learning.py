"""Social learning rules.

A rule receives the learners and, for each learner, a row of sampled role
models from the learner's group, and returns the variant each learner adopts.
Innovation is handled by the engine, not the rule: with probability
`innovation` a learner invents a variant instead of learning socially.

All rules are vectorised over learners. Parameters are plain dataclass fields,
so inference can address them by name, e.g. ``"learning.theta"``.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


class LearningRule:
    """Base class. Subclasses implement `choose(pop, learners, models)`."""

    def choose(self, pop, learners: np.ndarray, models: np.ndarray) -> np.ndarray:
        raise NotImplementedError


def _pick_by_count_weight(pool: np.ndarray, exponent: float, rng) -> np.ndarray:
    """For each row of `pool`, pick variant v with probability
    c_v^exponent / sum_w c_w^exponent, where c_v is the count of v in the row.

    Implemented by drawing one pool entry with weight c^(exponent - 1): a
    variant held c times then has total weight c * c^(exponent-1) = c^exponent.
    """
    counts = (pool[:, :, None] == pool[:, None, :]).sum(axis=2)
    w = counts ** (float(exponent) - 1.0)
    cw = np.cumsum(w, axis=1)
    target = rng.random(pool.shape[0]) * cw[:, -1]
    idx = np.minimum((cw <= target[:, None]).sum(axis=1), pool.shape[1] - 1)
    return pool[np.arange(pool.shape[0]), idx]


@dataclass(frozen=True)
class Neutral(LearningRule):
    """Unbiased (random) copying of one role model."""

    def choose(self, pop, learners, models):
        return pop.traits[models[:, 0]]


@dataclass(frozen=True)
class Conformity(LearningRule):
    """Frequency-dependent copying with conformity exponent theta.

    A learner adopts variant v with probability c_v^theta / sum_w c_w^theta,
    where c_v counts v among the sampled role models. theta = 1 is unbiased
    copying, theta > 1 conformity, theta < 1 anti-conformity.

    include_self=True also counts the learner's current variant (used in the
    longitudinal example of Deffner et al. 2024).
    """

    theta: float = 1.0
    include_self: bool = False

    def choose(self, pop, learners, models):
        pool = pop.traits[models]
        if self.include_self:
            pool = np.concatenate([pool, pop.traits[learners][:, None]], axis=1)
        return _pick_by_count_weight(pool, self.theta, pop.rng)


@dataclass(frozen=True)
class PayoffBias(LearningRule):
    """Payoff-biased imitation in a (frequency-dependent) game.

    Variants 0..k-1 are strategies. A variant's payoff in a group is
    ``payoffs[v] @ f_g`` where f_g are the variant frequencies in that group
    (a mean-field game within the group). Each learner compares its payoff with
    that of one random role model and switches to the model's variant with
    probability ``strength * (payoff_model - payoff_self)`` when positive
    (proportional imitation, Schlag 1998).

    In a large population the expected change is the discrete replicator
    equation  p_i' = p_i + strength * p_i * (pi_i - pi_bar),  which is tested
    in miras.theory. Requires a finite set of variants (Model.n_variants = k),
    and strength * (payoff range) <= 1 for the probabilities to be valid.
    """

    payoffs: tuple = ((1.0, 0.0), (0.0, 1.0))
    strength: float = 0.1

    def group_payoffs(self, pop):
        A = np.asarray(self.payoffs, float)
        k = A.shape[0]
        if pop.traits.max() >= k or pop.traits.min() < 0:
            raise ValueError("PayoffBias needs variants 0..k-1: set Model(n_variants=k)")
        freq = np.bincount(pop.group * k + pop.traits, minlength=pop.n_groups * k)
        freq = freq.reshape(pop.n_groups, k) / pop.group_size
        return freq @ A.T                                  # (n_groups, k) payoff of each variant

    def choose(self, pop, learners, models):
        pay = self.group_payoffs(pop)
        g = pop.group[learners]
        own = pop.traits[learners]
        other = pop.traits[models[:, 0]]
        p_switch = np.clip(self.strength * (pay[g, other] - pay[g, own]), 0.0, 1.0)
        return np.where(pop.rng.random(learners.size) < p_switch, other, own)


@dataclass(frozen=True)
class Mixture(LearningRule):
    """Each learning event uses rule i with probability weights[i].

    This models a population in which strategies are used in fixed proportions
    (e.g. 30% conformist, 70% payoff-biased learning events)."""

    rules: tuple = (Neutral(), Conformity(2.0))
    weights: tuple = (0.5, 0.5)

    def __post_init__(self):
        if len(self.rules) != len(self.weights):
            raise ValueError("rules and weights must have the same length")

    def choose(self, pop, learners, models):
        w = np.asarray(self.weights, float)
        which = pop.rng.choice(len(self.rules), size=learners.size, p=w / w.sum())
        out = pop.traits[learners].copy()
        for i, rule in enumerate(self.rules):
            sel = np.flatnonzero(which == i)
            if sel.size:
                out[sel] = rule.choose(pop, learners[sel], models[sel])
        return out
