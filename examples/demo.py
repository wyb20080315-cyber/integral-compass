"""Run after installing the package: python examples/demo.py."""

from integral_compass import analyze


def main():
    for expression in ("x**2 * exp(x)", "1/((x+1)*(x**2+1)**2)", "exp(-x**2)"):
        print(analyze(expression).explain())
        print()


if __name__ == "__main__":
    main()
