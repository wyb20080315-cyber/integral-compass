"""Bounded integration in an isolated worker process."""

import json
import math
import subprocess
import sys

import sympy as sp

from .models import IntegrationResult, IntegrationUndeterminedError, Step
from .parser import make_symbol, parse_expression


def analyze(expression: str | sp.Expr, variable: str | sp.Symbol = "x", *,
            timeout: float = 10.0) -> IntegrationResult:
    """Return an elementary/non_elementary/unknown result, with explanations.

    Strings use a real variable by default. For symbolic input, pass the same
    SymPy Symbol as ``variable`` to preserve its assumptions. Invalid input raises
    ExpressionError; a computation deadline returns unknown.
    """
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not (
            math.isfinite(timeout) and timeout > 0):
        raise ValueError("timeout must be a finite positive number of seconds")
    x = make_symbol(variable)
    f = parse_expression(expression, x)
    payload = {"expression": str(f), "variable": x.name, "assumptions": x.assumptions0}
    try:
        process = subprocess.run(
            [sys.executable, "-m", "integral_compass._worker"],
            input=json.dumps(payload), text=True, capture_output=True, timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return IntegrationResult("unknown", f, x, method="timeout", reason=
                                 f"Computation exceeded {timeout:g} seconds; no decision was made.")
    if process.returncode != 0:
        return IntegrationResult("unknown", f, x, method="backend_error", reason=
                                 "The integration backend failed; no mathematical decision was made.")
    try:
        data = json.loads(process.stdout)
        primitive = (parse_expression(data["antiderivative"], x)
                     if data["antiderivative"] is not None else None)
        return IntegrationResult(
            data["status"], f, x, primitive, data["method"], data["verified"], data["reason"],
            tuple(Step(s["title"], s["explanation"], s["expression"], tuple(s["rows"]))
                  for s in data["steps"]),
        )
    except (KeyError, TypeError, ValueError):
        return IntegrationResult("unknown", f, x, method="backend_error", reason=
                                 "The backend returned an unsupported result; no decision was made.")


def integrate(expression: str | sp.Expr, variable: str | sp.Symbol = "x", *,
              timeout: float = 10.0) -> sp.Expr | None:
    """Return an elementary primitive, None only for proven non-elementarity.

    Raise IntegrationUndeterminedError for unsupported cases or timeouts. Use
    analyze() to inspect those cases without catching an exception.
    """
    result = analyze(expression, variable, timeout=timeout)
    if result.status == "unknown":
        raise IntegrationUndeterminedError(result)
    return result.antiderivative
