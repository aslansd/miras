"""Analytic predictions the simulation engine is checked against.

These are derived independently of the engine, so agreement is evidence that
the engine implements the model it claims to. They assume WrightFisher
demography (every individual re-learns each step) and neutral copying unless
stated otherwise.
"""
from __future__ import annotations

import numpy as np


def island_identity(group_size: int, n_groups: int, migration: float, innovation: float,
                    tol: float = 1e-13, max_iter: int = 1_000_000):
    """Stationary probabilities of identity for the neutral island model.

    F0: two distinct individuals in the same group share a variant.
    F1: two individuals in different groups share a variant.

    Each step, migrants leave with probability m for a uniformly random other
    group; then everyone copies a uniformly random member of their current
    group (possibly themselves) and innovates a brand-new variant with
    probability mu. This is the process `Model` runs with WrightFisher
    demography, Neutral learning and n_variants=None.
    """
    N, d, m, mu = group_size, n_groups, migration, innovation
    F0 = F1 = 1.0
    keep = (1.0 - mu) ** 2
    for _ in range(max_iter):
        if d > 1:
            G0 = ((1 - m) ** 2 * F0 + 2 * m * (1 - m) * F1
                  + m ** 2 * (F0 + (d - 2) * F1) / (d - 1))
            same = (d - 2) / (d - 1) ** 2
            G1 = ((1 - m) ** 2 * F1 + 2 * m * (1 - m) * (F0 + (d - 2) * F1) / (d - 1)
                  + m ** 2 * (same * F0 + (1 - same) * F1))
        else:
            G0, G1 = F0, 0.0
        new0 = keep * (1.0 / N + (1.0 - 1.0 / N) * G0)
        new1 = keep * G1
        if abs(new0 - F0) + abs(new1 - F1) < tol:
            return new0, new1
        F0, F1 = new0, new1
    return F0, F1


def expected_homozygosity(group_size: int, innovation: float) -> float:
    """Expected sum of squared variant frequencies (counting self-pairs) in a
    single neutral Wright-Fisher population with infinite-alleles innovation.
    Exact solution of F = (1-mu)^2 [1/N + (1 - 1/N) F]."""
    N, mu = group_size, innovation
    keep = (1.0 - mu) ** 2
    F0 = keep / N / (1.0 - keep * (1.0 - 1.0 / N))
    return 1.0 / N + (1.0 - 1.0 / N) * F0


def expected_fst(group_size: int, n_groups: int, migration: float, innovation: float) -> float:
    """Expected cultural F_ST (Mesoudi's definition) in the neutral island
    model, as the ratio of expected total and within-group diversities.

    This is a ratio of expectations, whereas simulations average the ratio,
    so agreement is approximate (typically within a few percent for groups of
    50+ individuals)."""
    N, d = group_size, n_groups
    F0, F1 = island_identity(N, d, migration, innovation)
    sum_p2_within = 1.0 / N + (1.0 - 1.0 / N) * F0
    sum_p2_total = sum_p2_within / d + (1.0 - 1.0 / d) * F1
    H_w, H_t = 1.0 - sum_p2_within, 1.0 - sum_p2_total
    return (H_t - H_w) / H_t


def ewens_expected_variants(n: int, innovation: float, N: int | None = None) -> float:
    """Expected number of distinct variants among n individuals under the
    Ewens sampling formula, theta = 2 N mu for haploid Wright-Fisher copying
    (diffusion approximation; N defaults to n)."""
    N = n if N is None else N
    theta = 2.0 * N * innovation
    return float(np.sum(theta / (theta + np.arange(n))))


def replicator_step(p: np.ndarray, payoffs, strength: float) -> np.ndarray:
    """One step of the discrete replicator equation that PayoffBias
    (proportional imitation) follows in expectation:
    p_i' = p_i + strength * p_i * (pi_i - pi_bar), with pi = payoffs @ p."""
    A = np.asarray(payoffs, float)
    p = np.asarray(p, float)
    pi = A @ p
    return p + strength * p * (pi - p @ pi)


def replicator_trajectory(p0, payoffs, strength: float, n_steps: int) -> np.ndarray:
    out = [np.asarray(p0, float)]
    for _ in range(n_steps):
        out.append(replicator_step(out[-1], payoffs, strength))
    return np.array(out)


def mixed_equilibrium_2x2(payoffs) -> float:
    """Interior rest point (frequency of strategy 0) of a 2x2 game, e.g. the
    Hawk-Dove mixed equilibrium."""
    (a, b), (c, d) = np.asarray(payoffs, float)
    return (d - b) / (a - b - c + d)
