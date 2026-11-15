"""The 0.1 Risch-based contract, separate from depth-search semantics."""

from .api import _analyze
from .models import IntegrationUndeterminedError


def analyze(expression, variable="x", *, timeout=10.0):
    return _analyze(expression, variable, timeout=timeout, mode="classic")


def integrate(expression, variable="x", *, timeout=10.0):
    result = analyze(expression, variable, timeout=timeout)
    if result.status == "unknown":
        raise IntegrationUndeterminedError(result)
    return result.antiderivative
