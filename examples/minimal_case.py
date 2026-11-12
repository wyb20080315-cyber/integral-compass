"""Small, editable cases: run with the interpreter where the package is installed."""

import sympy as sp

from integral_compass import IntegralSolver, analyze, integrate


def main():
    print("CASE 1: x**2 * exp(x), depth 2 -> None")
    assert integrate("x**2*exp(x)", 2) is None
    print("PASS: all branches within depth 2 were exhausted.\n")

    print("CASE 2: same function, depth 3 -> verified primitive and DI steps")
    problem = IntegralSolver("x**2*exp(x)", 3)
    answer = problem.solve()
    x = problem.result.variable
    assert sp.simplify(sp.diff(answer, x) - x**2*sp.exp(x)) == 0
    print("PASS\n")

    print("CASE 3: log(x)/(x+1)**2 -> DI followed by actual partial fractions")
    problem = IntegralSolver("log(x)/(x+1)**2", 2)
    assert problem.solve() is not None
    assert problem.result.verified
    print("PASS\n")

    print("CASE 4: unsupported rule -> literal string 'unknown'")
    assert integrate("Abs(x)", 3) == "unknown"
    print("PASS\n")

    print("CASE 5: omit depth -> automatic Risch + unbounded-depth classroom search")
    assert analyze("x**2*exp(x)").verified
    print("PASS\n")

    print("CASE 6: cyclic integration by parts -> solve the equation for J")
    problem = IntegralSolver("exp(x)*sin(x)", 3)
    problem.solve()
    assert problem.result.verified
    assert any(step.title == "Solve cycle equation" for step in problem.result.steps)
    print("PASS\n")

    print("CASE 7: no depth specified -> Risch-proven non-elementarity")
    assert analyze("exp(-x**2)").status == "non_elementary"
    assert integrate("exp(-x**2)") is None
    print("PASS\nAll seven minimal cases passed.")


if __name__ == "__main__":
    main()
