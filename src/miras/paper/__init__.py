"""The three worked examples of Deffner, Fedorova, Andrews & McElreath (2024),
"Bridging theory and data: A computational workflow for cultural evolution",
PNAS 121(48), ported onto the miras engine.

    miras paper dags           # synthetic data from a DAG, power analysis
    miras paper abm            # migration x conformity ABM, Fig. 3
    miras paper longitudinal   # longitudinal Stan model, Fig. 4
    miras paper abc            # approximate Bayesian computation, Fig. 5

Original R code: https://github.com/DominikDeffner/CulturalEvolutionWorkflow (CC0).
"""
from ._model import paper_model

WORKFLOWS = {
    "dags": "miras.paper.dags",
    "abm": "miras.paper.abm",
    "longitudinal": "miras.paper.longitudinal",
    "abc": "miras.paper.abc",
}

__all__ = ["paper_model", "WORKFLOWS"]
