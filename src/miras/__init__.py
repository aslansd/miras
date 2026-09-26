"""miras -- cultural inheritance, simulated and interrogated.

Built on the workflow of Deffner, Fedorova, Andrews & McElreath (2024),
"Bridging theory and data: A computational workflow for cultural evolution",
PNAS 121(48). Please cite that paper when you use miras.
"""
__version__ = "0.1.1"

from .engine import (AgeStructured, Conformity, Islands, Mixture, Model, Neutral,
                     PayoffBias, Result, WrightFisher)
from .stats import CrossSectional, SUMMARIES, cultural_fst, summarize
from .inference import (ABCSMC, FunctionSimulator, LogUniform, ModelSimulator, Normal,
                        ReferenceTable, Uniform)
from .identify import IdentifiabilityReport, Thresholds, analyze, identify
from .provenance import tracked

__all__ = ["__version__", "Model", "Result", "Islands", "AgeStructured", "WrightFisher",
           "Neutral", "Conformity", "PayoffBias", "Mixture",
           "CrossSectional", "SUMMARIES", "cultural_fst", "summarize",
           "identify", "analyze", "IdentifiabilityReport", "Thresholds",
           "ModelSimulator", "FunctionSimulator", "ReferenceTable", "ABCSMC",
           "Uniform", "LogUniform", "Normal", "tracked"]
