"""Risch-only precheck; unsupported cases never imply non-elementarity."""

from sympy.integrals.risch import NonElementaryIntegral, risch_integrate

from .engine import _elementary, _verified
from .models import IntegrationResult, Step
from .parser import parse_expression


def risch_decision(f, x):
    try:
        primitive, remainder = risch_integrate(f, x, separate_integral=True)
    except (NotImplementedError, ValueError, TypeError, KeyError):
        return IntegrationResult("unknown", f, x, method="risch_unsupported",
                                 reason="The Risch backend did not decide this expression.")
    if isinstance(remainder, NonElementaryIntegral):
        return IntegrationResult(
            "non_elementary", f, x, method="risch",
            reason="Risch proved a non-elementary remainder. None here is a mathematical "
                   "non-elementarity decision, not a depth limit or absence of any primitive.",
            steps=(Step("Risch decision", "Certified non-elementary remainder.", str(remainder)),))
    if remainder == 0 and _elementary(primitive):
        parse_expression(str(primitive), x)
        if _verified(primitive, f, x):
            return IntegrationResult(
                "elementary", f, x, primitive, "risch", True,
                "Risch supplied an elementary primitive, verified by differentiation.",
                (Step("Risch primitive", "Use the supported exponential/logarithmic algorithm.",
                      str(primitive)), Step("Derivative check", "Simplify F'(x)-f(x).", "0")))
    return IntegrationResult("unknown", f, x, method="risch_unsupported",
                             reason="The Risch backend returned no verified decision.")
