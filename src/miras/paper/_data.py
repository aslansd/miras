"""Data files shipped with miras."""
from importlib import resources

import numpy as np


def age_migration_nl() -> np.ndarray:
    """Age-specific migration rates in the Netherlands (Fedorova et al. 2022),
    as used in Deffner et al. (2024). Index 0 = age 1."""
    with resources.files("miras.data").joinpath("beta_df.csv").open() as fh:
        return np.loadtxt(fh, delimiter=",", skiprows=1)[:, 1]
