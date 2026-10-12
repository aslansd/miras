"""The Model: structure + demography + learning rule + migration + innovation."""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

import numpy as np

from .learning import Conformity, LearningRule
from .population import Population, migration_vector
from .structure import AgeStructured, Islands, WrightFisher
from .. import stats


@dataclass
class Result:
    """Outcome of `Model.simulate`: recorded time series and the final state."""

    series: dict
    population: Population
    model: "Model"

    def summaries(self, names, design=None, rng=None):
        """Summary statistics of the final population, or of the sample a
        `design` (e.g. `CrossSectional`) would observe."""
        traits, group = self.population.traits, self.population.group
        if design is not None:
            traits, group = design.sample(traits, group, rng or self.population.rng)
        return stats.summarize(traits, group, names)


@dataclass(frozen=True)
class Model:
    """A cultural-evolution agent-based model.

    Parameters
    ----------
    structure : Islands
        Groups and their spatial arrangement.
    demography : AgeStructured | WrightFisher
        Births, deaths, and who learns each step.
    learning : LearningRule
        Neutral, Conformity, PayoffBias, Mixture, ...
    migration : float or sequence
        Per-step migration probability; a sequence is read as age-specific
        (index 0 = age 1).
    innovation : float
        Probability that a learning event produces an innovation.
    n_models : int
        Role models each learner samples from its group.
    n_variants : int or None
        None = infinite-alleles (every innovation is new); k = variants 0..k-1.
    initial : str or sequence
        'unique_per_group' (default), 'monomorphic', 'uniform', or initial
        variant frequencies.

    Any parameter, including nested ones, can be replaced by name:
    ``model.set({"learning.theta": 2.0, "migration": 0.1})``.
    """

    structure: Islands = field(default_factory=Islands)
    demography: object = field(default_factory=AgeStructured)
    learning: LearningRule = field(default_factory=Conformity)
    migration: object = 0.0
    innovation: float = 0.05
    n_models: int = 30
    n_variants: int | None = None
    initial: object = "unique_per_group"

    # ---------------------------------------------------------------- #
    def set(self, params: dict | None = None, **kwargs) -> "Model":
        """Return a copy with parameters replaced; dotted names reach into
        components (``"learning.theta"``, ``"structure.r_dist"``)."""
        params = {**(params or {}), **kwargs}
        model = self
        for name, value in params.items():
            model = _replace_path(model, name.split("."), value)
        return model

    def get(self, name: str):
        obj = self
        for part in name.split("."):
            obj = getattr(obj, part)
        return obj

    def new_population(self, rng) -> Population:
        s = self.structure
        grid = s.make_grid(rng)
        return Population(
            rng=rng, n_groups=s.n_groups, group_size=s.group_size,
            ages=self.demography.initial_ages(rng, s.N), dist=s.distances(grid),
            r_dist=s.r_dist, n_variants=self.n_variants, initial=self.initial,
        )

    def simulate(self, n_steps: int, *, burn_in: int = 0, seed=None, rng=None,
                 record=("fst",), every: int = 1) -> Result:
        """Run the model.

        `burn_in` steps of demography only (no migration or learning) let an
        age-structured population reach its stable age distribution; then
        `n_steps` steps of full dynamics. Each full step is:
        demography -> migration -> social learning (+ innovation).
        Entries of `record` (summary names from miras.SUMMARIES, or callables
        ``f(traits, group) -> float``) are computed every `every` steps.
        """
        if n_steps < 1:
            raise ValueError("n_steps must be >= 1")
        rng = rng if rng is not None else np.random.default_rng(seed)
        if self.n_models > self.structure.group_size:
            raise ValueError("n_models cannot exceed structure.group_size")
        pop = self.new_population(rng)
        max_age = getattr(self.demography, "max_age", 1)
        m_vec = migration_vector(self.migration, max_age)
        # record entries are summary names or callables f(traits, group) -> float
        fns = [(r, stats.SUMMARIES[r]) if isinstance(r, str) else (getattr(r, "__name__", "custom"), r)
               for r in (record or ())]
        n_rec = (n_steps + every - 1) // every
        series = {name: np.zeros(n_rec) for name, _ in fns}

        for t in range(burn_in + n_steps):
            self.demography.step(pop)
            if t < burn_in:
                continue
            pop.migrate(m_vec)
            learners = self.demography.learners(pop)
            if learners.size:
                models = pop.sample_models(learners, self.n_models)
                new = self.learning.choose(pop, learners, models)
                pop.update(learners, new, self.innovation)
            s = t - burn_in
            if fns and s % every == 0:
                for name, fn in fns:
                    series[name][s // every] = fn(pop.traits, pop.group)
        return Result(series=series, population=pop, model=self)


def _replace_path(obj, path, value):
    head = path[0]
    if not dataclasses.is_dataclass(obj) or head not in {f.name for f in dataclasses.fields(obj)}:
        raise AttributeError(f"{type(obj).__name__} has no parameter '{head}'")
    if len(path) == 1:
        return dataclasses.replace(obj, **{head: value})
    return dataclasses.replace(obj, **{head: _replace_path(getattr(obj, head), path[1:], value)})


__all__ = ["Model", "Result", "Islands", "AgeStructured", "WrightFisher"]
