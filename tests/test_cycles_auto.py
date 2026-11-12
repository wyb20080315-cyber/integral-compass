import pytest
import sympy as sp

from integral_compass import analyze, integrate
from integral_compass.models import IntegrationResult


@pytest.mark.parametrize("expression,depth", [
    ("exp(x)*sin(x)", 3),
    ("exp(2*x)*sin(3*x)", 3),
    ("-5*sin(x)*cos(x)", 2),
    ("sin(x)*cos(x)", 2),
])
def test_cycles_keep_path_coefficients_and_solve_at_the_boundary(expression, depth):
    result = analyze(expression, depth)
    assert result.status == "elementary", result.explain()
    assert result.verified
    assert result.depth_reached <= depth
    assert any(step.title == "Solve cycle equation" for step in result.steps)
    assert sp.simplify(sp.trigsimp(sp.diff(result.antiderivative, result.variable)
                                 - result.integrand)) == 0


def test_a_cycle_does_not_bypass_decision_depth():
    assert analyze("exp(x)*sin(x)", 2).status == "exhausted"
    assert analyze("exp(x)*sin(x)", 3).status == "elementary"


def test_degenerate_cycle_is_not_mistaken_for_a_solution():
    result = analyze("x**3*exp(x)", 3)
    assert result.status == "exhausted"
    assert result.search_complete
    assert any("Degenerate cycle" in node.get("reason", "") for node in result.search_tree)
    assert analyze("x**3*exp(x)", 4).status == "elementary"


def test_linearity_preserves_independent_cycle_equations():
    result = analyze("exp(x)*sin(x) + x*exp(x)", 3)
    assert result.status == "elementary", result.explain()
    assert result.verified


def test_default_auto_mode_can_prove_nonelementarity():
    result = analyze("exp(-x**2)")
    assert result.status == "non_elementary"
    assert result.method == "risch"
    assert integrate("exp(-x**2)") == "None, verified by Risch"
    assert not result.search_complete  # It is a Risch decision, not exhausted search.


def test_default_auto_mode_prefers_actual_classroom_steps_when_available():
    result = analyze("x**2*exp(x)")
    assert result.status == "elementary"
    assert result.method == "parts_search"
    assert any(step.title == "DI / integration by parts" for step in result.steps)


@pytest.mark.parametrize("options", [{"depth": 2}, {"depth": 2, "timeout": 10}])
def test_an_explicit_limit_selects_search_without_a_risch_bypass(monkeypatch, options):
    from integral_compass import api

    calls = []
    x = sp.Symbol("x", real=True)

    def fake(expression, variable, **kwargs):
        calls.append(kwargs)
        return IntegrationResult("unknown", x, x, reason="test search")

    monkeypatch.setattr(api, "_analyze", fake)
    assert api.analyze("x", **options).status == "unknown"
    assert len(calls) == 1
    assert calls[0].get("mode", "search") == "search"


def test_explicit_timeout_keeps_risch_when_depth_is_omitted():
    result = analyze("exp(-x**2)", timeout=20)
    assert result.status == "non_elementary"
    assert result.method == "risch"


def test_auto_uses_a_verified_risch_answer_if_step_search_is_unknown(monkeypatch):
    from integral_compass import api

    x = sp.Symbol("x", real=True)
    responses = iter([
        IntegrationResult("elementary", sp.exp(x), x, sp.exp(x), "risch", True),
        IntegrationResult("unknown", sp.exp(x), x, method="timeout", reason="test timeout"),
    ])
    monkeypatch.setattr(api, "_analyze", lambda *a, **kw: next(responses))
    result = api.analyze("exp(x)")
    assert result.status == "elementary"
    assert result.method == "risch_fallback"
    assert result.verified
    assert result.antiderivative == sp.exp(x)


def test_an_unproven_risch_integral_is_unknown(monkeypatch):
    from integral_compass import risch_backend

    x = sp.Symbol("x", real=True)
    monkeypatch.setattr(risch_backend, "risch_integrate", lambda *a, **kw: (0, sp.Integral(sp.sin(x), x)))
    assert risch_backend.risch_decision(sp.sin(x), x).status == "unknown"


def test_unknown_stays_unknown_if_both_engines_are_undecided():
    assert analyze("Abs(x)").status == "unknown"
    assert integrate("Abs(x)").startswith("unknown, unsupported rule:")
