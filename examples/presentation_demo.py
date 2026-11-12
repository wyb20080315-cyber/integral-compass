"""Five concise rows for a one-minute live demo; detailed steps are opt-in."""

import argparse

from integral_compass import IntegralSolver, integrate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", action="store_true", help="Also show DI and partial-fraction steps")
    args = parser.parse_args()
    for label, expression, depth in [
        ("DI", "x*exp(x)", 2),
        ("Partial fractions", "1/(x*(x+1))", 1),
        ("Depth exhausted", "x*exp(x)", 1),
        ("Risch decision", "exp(-x**2)", None),
        ("Unsupported rule", "Abs(x)", 1),
    ]:
        value = integrate(expression, depth, show_steps=False)
        print(f"{label}: {expression}, depth={depth} -> {value!r}")
    if args.steps:
        IntegralSolver("x*exp(x)", 2).solve()
        IntegralSolver("1/(x*(x+1))", 1).solve()


if __name__ == "__main__":
    main()
