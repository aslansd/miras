"""Population structure and demography.

Structure says *where* individuals live and how they move between groups.
Demography says *who* is born, who dies, and who updates their cultural
variant in a given step.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# --------------------------------------------------------------------------- #
# Structure
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Islands:
    """`n_groups` equally sized groups (villages) placed on a spatial grid.

    Migrants choose a destination group with probability proportional to
    exp(-r_dist * distance); r_dist = 0 means any other group equally likely
    (the island model). Group sizes are conserved: migrants only fill slots
    vacated by other migrants, as in Deffner et al. (2024).
    """

    n_groups: int = 30
    group_size: int = 100
    size_grid: int = 50
    r_dist: float = 0.0

    @property
    def N(self) -> int:
        return self.n_groups * self.group_size

    def make_grid(self, rng: np.random.Generator) -> np.ndarray:
        """Village labels 1..n_groups on a size_grid x size_grid grid (0 = empty)."""
        cells = self.size_grid * self.size_grid
        if self.n_groups > cells:
            raise ValueError("more groups than grid cells")
        grid = np.zeros(cells, dtype=int)
        grid[rng.choice(cells, self.n_groups, replace=False)] = rng.permutation(self.n_groups) + 1
        return grid.reshape(self.size_grid, self.size_grid, order="F")

    def distances(self, grid: np.ndarray) -> np.ndarray:
        coords = np.array([np.argwhere(grid == g + 1)[0] for g in range(self.n_groups)], float)
        diff = coords[:, None, :] - coords[None, :, :]
        return np.sqrt((diff ** 2).sum(-1))


# --------------------------------------------------------------------------- #
# Demography
# --------------------------------------------------------------------------- #
def f_age(increasing: bool, rate: float, age):
    """Exponential age dependence used for survival and learning."""
    age = np.asarray(age, dtype=float)
    if increasing:
        return 1.0 - np.exp(-rate * (age - 1.0))
    return np.exp(-rate * (age - 1.0))


@dataclass(frozen=True)
class WrightFisher:
    """Non-overlapping generations: every individual updates every step and
    nobody is born or dies. With neutral copying this is the Wright-Fisher
    model, which is what makes the analytic checks in `miras.theory` exact."""

    def initial_ages(self, rng, N):
        return np.ones(N, dtype=np.int64)

    def step(self, pop):
        return np.empty(0, dtype=np.int64)

    def learners(self, pop):
        return np.arange(pop.N)


@dataclass(frozen=True)
class AgeStructured:
    """Overlapping generations with age-dependent survival and learning, as in
    Deffner et al. (2024).

    Each step individuals survive with probability exp(-r_mort * (age - 1))
    (and die at max_age). Their slots are filled by newborns who copy the
    variant of a random adult (age >= adult_age) survivor in the same group
    (vertical transmission). Individuals update socially with probability
    exp(-r_learn * (age - 1)).

    legacy_aging=True reproduces a quirk of the original R code, in which
    nobody in a group ages in a year when nobody in that group died.
    """

    r_mort: float = 0.001
    max_age: int = 90
    adult_age: int = 18
    r_learn: float = 0.03
    initial_max_age: int = 80
    legacy_aging: bool = False

    def initial_ages(self, rng, N):
        return rng.integers(1, self.initial_max_age + 1, N)

    def step(self, pop):
        rng = pop.rng
        alive = rng.random(pop.N) < f_age(False, self.r_mort, pop.age)
        alive[pop.age >= self.max_age] = False
        babies = np.flatnonzero(~alive)
        if babies.size:
            eligible = np.flatnonzero(alive & (pop.age >= self.adult_age))
            eligible = eligible[np.argsort(pop.group[eligible], kind="stable")]
            counts = np.bincount(pop.group[eligible], minlength=pop.n_groups)
            offsets = np.concatenate(([0], np.cumsum(counts)[:-1]))
            g = pop.group[babies]
            if np.any(counts[g] == 0):
                raise RuntimeError("a group has no adult survivors to reproduce")
            parents = eligible[offsets[g] + (rng.random(babies.size) * counts[g]).astype(int)]
            pop.traits[babies] = pop.traits[parents]
        grow = alive.copy()
        if self.legacy_aging:
            has_babies = np.bincount(pop.group[babies], minlength=pop.n_groups) > 0
            grow &= has_babies[pop.group]
        pop.age[grow] += 1
        pop.age[babies] = 1
        return babies

    def learners(self, pop):
        return np.flatnonzero(pop.rng.random(pop.N) < f_age(False, self.r_learn, pop.age))
