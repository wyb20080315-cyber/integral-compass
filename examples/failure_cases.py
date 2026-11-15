"""Minimal real failure outcomes; --internal adds clearly simulated software faults."""

import argparse

from integral_compass import integrate


def show(label, expression, depth=None, **kwargs):
    arguments = [repr(expression)]
    if depth is not None:
        arguments.append(repr(depth))
    arguments.extend(f"{key}={value!r}" for key, value in kwargs.items())
    print(f"\n{label}\n  integrate({', '.join(arguments)})")
    value = integrate(expression, depth, show_steps=False, **kwargs)
    print(f"  -> {value!r}  [type: {type(value).__name__}]")
    return value


def real_cases():
    assert show("1. Depth exhausted", "x*exp(x)", 1) is None
    assert show("2. No elementary primitive (Risch)", "exp(-x**2)") == "None, verified by Risch"
    assert show("3. Timeout (deliberately tiny budget)", "x", 1,
                timeout=0.000001).startswith("unknown, timeout:")
    assert show("4. Unsupported rule", "Abs(x)", 1).startswith("unknown, unsupported rule:")
    assert show("5. Unresolved branches", "log(x)**2", 2).startswith("unknown, unresolved branches:")
    # This confirms that unresolved is not a claim that the integral is impossible.
    recovered = integrate("log(x)**2", 3, show_steps=False)
    assert not isinstance(recovered, str) and recovered is not None
    print("  Increasing depth to 3 succeeds:", recovered)
    print("\nInput mistakes are exceptions, not mathematical failure outcomes:")
    for label, expression, depth, options in [
        ("division by zero", "1/0", 1, {}),
        ("invalid depth", "x", 0, {}),
        ("invalid timeout", "x", 1, {"timeout": 0}),
    ]:
        try:
            integrate(expression, depth, show_steps=False, **options)
        except ValueError as error:
            print(f"  {label}: {type(error).__name__}: {error}")
        else:
            raise AssertionError("Invalid input was accepted")


def internal_faults():
    # These are explicit fault injections, not claims about the displayed functions.
    import subprocess
    from unittest.mock import patch

    import sympy as sp

    from integral_compass.search import search_core

    print("\nSIMULATED software faults (not mathematical examples):")
    for label, code, output in [("worker crash", 1, ""), ("invalid worker response", 0, "not-json")]:
        with patch("integral_compass.api.subprocess.run",
                   return_value=subprocess.CompletedProcess([], code, stdout=output, stderr="")):
            value = integrate("x", 1, show_steps=False)
        assert value.startswith("unknown, backend error:")
        print(f"  {label}: {value}")
    x = sp.Symbol("x", real=True)
    with patch("integral_compass.search._verified", side_effect=[True, False]):
        result = search_core(x, x, 1)
    assert result.value.startswith("unknown, verification failed:")
    print("  forced derivative-check failure:", result.value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--internal", action="store_true")
    args = parser.parse_args()
    real_cases()
    if args.internal:
        internal_faults()
    print("\nAll failure cases behaved as documented.")


if __name__ == "__main__":
    main()
