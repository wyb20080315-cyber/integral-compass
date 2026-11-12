import json
import subprocess
import sys

import pytest
import sympy as sp

from integral_compass import (
    ExpressionError,
    IntegrationUndeterminedError,
    analyze,
    integrate,
)


@pytest.mark.parametrize("expression,method", [
    ("0", "polynomial"),
    ("7", "polynomial"),
    ("x**3 - 2*x + 1/3", "polynomial"),
    ("x**2 * exp(x)", "di"),
    ("(x**3 + 2*x) * exp(-2*x+1)", "di"),
    ("x**2 * sin(3*x+2)", "di"),
    ("(2*x+1) * cos(-2*x)", "di"),
    ("1/x", "partial_fractions"),
    ("1/((x+1)*(x**2+1)**2)", "partial_fractions"),
    ("(x**4+2)/(x**2-1)", "partial_fractions"),
    ("(3*x+2)/(x-1)**3", "partial_fractions"),
    ("2*x*exp(x**2)", "risch"),
    ("1/(x*log(x))", "risch"),
    ("sin(x)**3 * cos(x)", "sympy_fallback"),
    ("1/sqrt(1-x**2)", "sympy_fallback"),
])
def test_elementary_examples(expression, method):
    result = analyze(expression)
    assert result.status == "elementary", result.explain()
    assert result.method == method
    assert result.verified
    assert result.antiderivative is not None
    # Independently sample the derivative on both sides, away from singularities.
    for point in (sp.Rational(-23, 10), sp.Rational(17, 10)):
        residual = (sp.diff(result.antiderivative, result.variable)
                    - result.integrand).subs(result.variable, point).evalf()
        assert abs(complex(residual)) < 1e-9


@pytest.mark.parametrize("expression", ["exp(-x**2)", "exp(x)/x", "1/log(x)",
                                         "x + exp(-x**2)"])
def test_only_proven_nonelementary_returns_none(expression):
    result = analyze(expression)
    assert result.status == "non_elementary", result.explain()
    assert result.method == "risch"
    assert result.antiderivative is None
    assert not result.verified
    assert integrate(expression) is None


def test_di_rows_and_negative_slope():
    result = analyze("x**2 * sin(-2*x)")
    rows = result.steps[0].rows
    assert [row["sign"] for row in rows] == ["+", "-", "+", "stop"]
    assert rows[0]["D"] == "-x**2"  # sin(-2*x) canonicalizes to -sin(2*x)
    assert rows[-1]["D"] == "0"


def test_repeated_quadratic_decomposition_is_exact():
    result = analyze("1/((x+1)*(x**2+1)**2)")
    from integral_compass.parser import parse_expression
    decomposition = parse_expression(result.steps[1].expression, result.variable)
    assert sp.cancel(decomposition - result.integrand) == 0
    assert "(x**2 + 1)**2" in result.steps[1].expression


def test_real_log_preserves_negative_interval():
    result = analyze("1/x")
    assert result.antiderivative == sp.log(sp.Abs(result.variable))
    assert result.antiderivative.subs(result.variable, -2) == sp.log(2)


def test_custom_symbol_and_assumptions():
    t = sp.Symbol("t", positive=True)
    answer = integrate(t**2 * sp.exp(t), t)
    assert sp.simplify(sp.diff(answer, t) - t**2 * sp.exp(t)) == 0
    assert analyze("t**2", "t").status == "elementary"


def test_timeout_is_unknown_and_never_none():
    result = analyze("exp(-x**2)", timeout=0.000001)
    assert result.status == "unknown"
    assert result.method == "timeout"
    with pytest.raises(IntegrationUndeterminedError) as error:
        integrate("exp(-x**2)", timeout=0.000001)
    assert error.value.result.status == "unknown"


def test_unsupported_abs_is_unknown():
    result = analyze("Abs(x)")
    assert result.status == "unknown"
    with pytest.raises(IntegrationUndeterminedError):
        integrate("Abs(x)")


@pytest.mark.parametrize("expression", [
    "__import__('os').system('id')", "x.__class__", "[x][0]", "lambda: x",
    "open('a')", "y+x", "sin(x, x)", "1/0", "x^2", "x**1000000",
    "True", "", "nan", "1e999", "sqrt(-1)/0",
])
def test_invalid_or_executable_input_is_rejected(expression):
    with pytest.raises(ExpressionError):
        analyze(expression)


@pytest.mark.parametrize("timeout", [0, -1, float("inf"), float("nan"), True, "10"])
def test_invalid_timeout(timeout):
    with pytest.raises(ValueError):
        analyze("x", timeout=timeout)


def test_cli_json_and_exit_codes():
    command = [sys.executable, "-m", "integral_compass"]
    success = subprocess.run(command + ["x*exp(x)", "--json"],
                             capture_output=True, text=True, check=False)
    assert success.returncode == 0
    assert json.loads(success.stdout)["verified"]
    unknown = subprocess.run(command + ["x", "--timeout", "0.000001", "--json"],
                             capture_output=True, text=True, check=False)
    assert unknown.returncode == 3
    assert json.loads(unknown.stdout)["status"] == "unknown"
    invalid = subprocess.run(command + ["bad(x)"], capture_output=True, text=True, check=False)
    assert invalid.returncode == 2


def test_result_json_and_explanation():
    result = analyze("x*exp(x)")
    assert json.loads(json.dumps(result.to_dict()))["status"] == "elementary"
    assert "DI table" in result.explain()
    assert "+ C" in result.explain()


def test_unevaluated_integral_is_not_a_nonelementarity_certificate(monkeypatch):
    from integral_compass import engine

    x = sp.Symbol("x", real=True)
    f = sp.sin(x**2)
    ordinary_integral = sp.Integral(f, x)
    monkeypatch.setattr(engine, "risch_integrate", lambda *a, **kw: (0, ordinary_integral))
    monkeypatch.setattr(engine.sp, "integrate", lambda *a, **kw: ordinary_integral)
    assert engine.analyze_core(f, x).status == "unknown"


def test_wrong_elementary_candidate_must_pass_verification(monkeypatch):
    from integral_compass import engine

    x = sp.Symbol("x", real=True)
    f = sp.exp(x**2)
    monkeypatch.setattr(engine, "risch_integrate", lambda *a, **kw: (x, 0))
    monkeypatch.setattr(engine.sp, "integrate", lambda *a, **kw: x)
    assert engine.analyze_core(f, x).status == "unknown"
