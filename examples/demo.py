"""Run after installing the package: python examples/demo.py."""

from integral_compass import IntegralSolver, integrate


def main():
    print("Depth 2:", integrate("x**2*exp(x)", 2))
    IntegralSolver("x**2*exp(x)", 3).solve()
    IntegralSolver("log(x)/(x+1)**2", 2).solve()
    print("Unsupported:", integrate("Abs(x)", 3))


if __name__ == "__main__":
    main()
