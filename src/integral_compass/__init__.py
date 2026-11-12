"""Integral Compass: explainable elementary integration for calculus students."""

from .api import IntegralSolver, analyze, integrate
from .models import IntegrationResult, IntegrationUndeterminedError, Step
from .parser import ExpressionError

__version__ = "0.4.0"
__all__ = [
           "ExpressionError",
           "IntegralSolver",
           "IntegrationResult",
           "IntegrationUndeterminedError",
           "Step",
           "analyze",
           "integrate",
]
