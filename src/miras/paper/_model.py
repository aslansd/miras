"""The model of Deffner et al. (2024), expressed with the miras engine."""
from ..engine import AgeStructured, Conformity, Islands, Model


def paper_model(theta=1.0, m=0.1, mu=0.05, *, r_learn=0.03, r_mort=0.001, max_age=90,
                n_groups=30, group_size=100, n_models=30, size_grid=50, r_dist=0.0,
                include_self=False, legacy_aging=False) -> Model:
    """3000 agents in 30 villages of 100, age-structured demography, conformist
    learning from 30 role models, migration (scalar or age-specific) and
    innovation, exactly as in ConDiv_ABM.R / ABC_analysis.R."""
    return Model(
        structure=Islands(n_groups=n_groups, group_size=group_size, size_grid=size_grid, r_dist=r_dist),
        demography=AgeStructured(r_mort=r_mort, max_age=max_age, r_learn=r_learn,
                                 legacy_aging=legacy_aging),
        learning=Conformity(theta=theta, include_self=include_self),
        migration=m, innovation=mu, n_models=n_models,
    )
