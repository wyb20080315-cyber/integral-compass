import json
import subprocess
import sys
from collections import Counter

import pytest
import sympy as sp

from integral_compass import IntegralSolver, analyze, integrate


def test_root_is_level_one_and_depth_changes_the_result():
    shallow = analyze("x**2*exp(x)", 2)
    assert shallow.status == "exhausted"
    assert shallow.search_complete
    assert shallow.depth_reached == 2
    assert integrate("x**2*exp(x)", 2) is None
    deep = analyze("x**2*exp(x)", 3)
    assert deep.status == "elementary"
    assert deep.verified
    assert deep.depth_reached == 3
    assert sp.simplify(sp.diff(deep.antiderivative, deep.variable) - deep.integrand) == 0


def test_both_directions_and_all_four_third_level_leaves():
    result = analyze("x**3*exp(x)", 3)
    assert result.status == "exhausted"
    assert result.search_complete
    assert Counter(node["depth"] for node in result.search_tree) == {1: 1, 2: 2, 3: 4}
    second_level = [n for n in result.search_tree if n["depth"] == 2]
    assert second_level[0]["u"] == second_level[1]["dv"]
    assert second_level[0]["dv"] == second_level[1]["u"]
    assert analyze("x**3*exp(x)", 4).status == "elementary"


def test_reverse_direction_can_succeed_after_first_is_unknown():
    result = analyze("log(x)/(x+1)**2", 2)
    assert result.status == "elementary"
    assert any(n["status"] == "unknown" for n in result.search_tree)
    assert any(s.title == "DI / integration by parts" for s in result.steps)
    assert any(s.title == "Partial fractions" for s in result.steps)
    residual = sp.diff(result.antiderivative, result.variable) - result.integrand
    # Absolute-log derivatives are local identities away from their zeros;
    # generic simplification can retain sign/Abs instead of returning zero.
    for point in (sp.Rational(1, 2), sp.Rational(7, 3), sp.Integer(-2)):
        assert abs(complex(residual.subs(result.variable, point).evalf())) < 1e-12


@pytest.mark.parametrize("expression", ["x**2*exp(x)", "x**2*sin(3*x+2)",
                                         "x*cos(-2*x)", "log(x)"])
def test_no_depth_limit_finds_a_verified_path(expression):
    result = analyze(expression)
    assert result.status == "elementary", result.explain()
    assert result.search_depth is None
    assert result.verified


def test_rational_leaf_succeeds_even_at_depth_one():
    result = analyze("1/((x+1)*(x**2+1)**2)", 1)
    assert result.status == "elementary"
    assert result.depth_reached == 1
    assert any(s.title == "Partial fractions" for s in result.steps)


def test_unresolved_branch_propagates_unknown_instead_of_none():
    assert analyze("Abs(x)", 3).status == "unknown"
    assert integrate("Abs(x)", 3).startswith("unknown, unsupported rule:")
    # A solvable cycle is now resolved instead of being reported as unknown.
    result = analyze("sin(x)*cos(x)")
    assert result.status == "elementary"
    assert result.verified
    assert not result.search_complete


def test_timeout_is_unknown_even_when_the_problem_is_solvable():
    result = analyze("x*exp(x)", 3, timeout=0.000001)
    assert result.status == "unknown"
    assert result.method == "timeout"
    assert integrate("x*exp(x)", 3, timeout=0.000001).startswith("unknown, timeout:")


@pytest.mark.parametrize("depth", [0, -1, True, False, 2.5, "3", sp.Integer(3)])
def test_depth_must_be_a_positive_python_int_or_none(depth):
    with pytest.raises(ValueError):
        analyze("x", depth)


def test_class_prints_only_success_and_reuses_its_result(capsys, monkeypatch):
    problem = IntegralSolver("log(x)/(x+1)**2", 2)
    answer = problem.solve()
    output = capsys.readouterr().out
    assert "DI / integration by parts" in output
    assert "Partial fractions" in output
    assert "+ C" in output
    assert problem.result.verified
    from integral_compass import api
    monkeypatch.setattr(api, "analyze", lambda *a, **kw: pytest.fail("unexpected recomputation"))
    assert problem.solve(show_steps=False) == answer
    assert not capsys.readouterr().out
    problem.show_tree()
    assert "depth=2" in capsys.readouterr().out


def test_function_printing_can_be_disabled(capsys):
    assert integrate("x*exp(x)", 1) is None
    assert capsys.readouterr().out == ""
    assert integrate("x*exp(x)", 2, show_steps=False) is not None
    assert capsys.readouterr().out == ""
    integrate("x*exp(x)", 2)
    assert "DI / integration by parts" in capsys.readouterr().out


def test_custom_symbol_is_now_keyword_only():
    t = sp.Symbol("t", positive=True)
    result = analyze(t*sp.exp(t), 2, variable=t)
    assert result.variable == t
    assert result.verified


def test_linearity_does_not_consume_a_parts_level():
    result = analyze("x*exp(x) + x*sin(x)", 2)
    assert result.status == "elementary"
    assert result.depth_reached == 2
    assert analyze("sin(x) + cos(x)", 1).status == "elementary"


def test_unsupported_rational_degree_is_unknown_not_exhausted():
    assert analyze("x**31", 1).status == "unknown"


def test_search_cli_depth_json_and_unknown_exit_code():
    command = [sys.executable, "-m", "integral_compass"]
    run = subprocess.run(command + ["x**2*exp(x)", "--depth", "2", "--json"],
                         capture_output=True, text=True, check=False)
    assert run.returncode == 0
    data = json.loads(run.stdout)
    assert data["status"] == "exhausted"
    assert data["search_depth"] == 2
    assert len(data["search_tree"]) == 3
    run = subprocess.run(command + ["Abs(x)", "--depth", "3", "--json"],
                         capture_output=True, text=True, check=False)
    assert run.returncode == 3


def test_no_classic_fallback_can_bypass_the_depth(monkeypatch):
    from integral_compass import search

    monkeypatch.setattr(sp, "integrate", lambda *a, **kw: pytest.fail("general integrator called"))
    x = sp.Symbol("x", real=True)
    # No rational leaves are integrated at this boundary, so the backend must stay unused.
    result = search.search_core(x**2*sp.exp(x), x, 1)
    assert result.status == "exhausted"
