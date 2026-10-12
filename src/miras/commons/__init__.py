"""miras.commons: a common-pool resource shared by culturally different
groups, and how to seed a resource-saving innovation so that it spreads.

See the model specification (September 2026) for the design and the
decisions behind it.
"""
from .model import (NONE, OUTSIDE, CommonsModel, CommonsResult, Group, Innovation, Learning,
                    Mechanisms, Resource, Seeding, gini)

__all__ = ["CommonsModel", "CommonsResult", "Group", "Innovation", "Learning", "Mechanisms",
           "Resource", "Seeding", "gini", "NONE", "OUTSIDE"]
