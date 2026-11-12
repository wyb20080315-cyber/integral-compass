# Integral Compass 🧭

**Explore both integration-by-parts directions. Follow the successful path.**

Version 0.2 adds depth-controlled classroom integration. The original integral is
level **1**; each integration-by-parts decision advances one level. The second
argument is `depth=None`, meaning no depth cap. A separate 10-second worker deadline
still applies, so an unending search returns `"unknown"` instead of hanging forever.

[中文指南](docs/guide.zh-CN.md) · [Windows installation](docs/windows.zh-CN.md) ·
[API](docs/api.md) · [Mathematics](docs/mathematics.md) · [One-minute demo](docs/demo.zh-CN.md)

## Why this project?

The idea came from a student's own calculus notes: can a program follow DI and
partial fractions, explore choices, and show why a particular integration works?
Our contribution is the search strategy, depth semantics, inspectable tree,
class-based explanation and exact derivative check. SymPy supplies algebra,
partial-fraction decomposition and rational-term integration. The classic Risch
backend remains available separately; we do not claim to implement full Risch.

## Install from source

Requires Python 3.10+. PyPI publication is currently deferred.

```bash
git clone https://github.com/wyb20080315-cyber/integral-compass.git
cd integral-compass
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows: use .venv\Scripts\python.exe directly instead of activating.
python -m pip install .
```

If testing a development branch, check out that branch first. For a wheel downloaded
from this chat: `python -m pip install path/to/integral_compass-0.2.0-py3-none-any.whl`.
The offline Windows test kit includes that wheel and its dependencies.

## Return values

```python
from integral_compass import integrate, analyze, IntegralSolver

assert integrate("x**2 * exp(x)", 2) is None
F = integrate("x**2 * exp(x)", 3)  # prints the successful steps automatically
assert integrate("Abs(x)", 3) == "unknown"

# Omit depth: fair iterative-deepening search, with no configured depth cap.
F = integrate("x**2 * exp(x)", show_steps=False)

problem = IntegralSolver("log(x)/(x+1)**2", 2)
F = problem.solve()     # prints both DI and actual partial fractions on this path
problem.show_tree()    # includes failed/unknown directions that were explored
report = problem.result
assert report.verified
```

| `analyze(...).status` | `integrate(...)` | Meaning |
| --- | --- | --- |
| `elementary` | SymPy expression, without `C` | A solution passed derivative verification |
| `exhausted` | `None` | Every generated branch within the specified depth failed |
| `unknown` | the string `"unknown"` | A branch could not be evaluated, a cycle was unresolved, the worker failed, or time ran out |

**In 0.2 search mode, `None` is not proof that an elementary primitive does not exist.**
For example, the same `x**2*exp(x)` returns `None` at depth 2 and succeeds at depth 3.
A success prints only the steps actually used; a basic-table-only solution does not
invent a partial-fractions derivation. `analyze()` is silent and returns structured data.

## What does the search explore?

For `u * g`, try both `D=u, I=g` and `D=g, I=u`. Once a side primitive `v` is
available, recurse on `u' * v` and recombine `u*v - integral(u'*v)`.
A side primitive must come from the explicit basic table or rational terminal rules.
If unavailable, that direction is unknown. A different direction may still succeed.

At each level, rational functions can finish via polynomial division and partial
fractions. Polynomials, affine rational powers and linear-argument exp/sin/cos also
have terminal rules. These base rules are necessary even for a simple DI example.
Sums are handled by linearity without spending a parts level.

Products with more than two canonical factors try all nonempty factor bipartitions,
in both orientations, up to eight factors. “All branches” means this finite grammar,
not every mathematically possible rewriting or substitution. Risch/general SymPy
integration cannot bypass the requested depth in search mode. See the mathematics guide.

## CLI and minimal examples

```bash
integral-compass 'x**2*exp(x)' --depth 2
integral-compass 'x**2*exp(x)' --depth 3 --json
integral-compass 'log(x)/(x+1)**2' --depth 2
python examples/minimal_case.py
```

CLI exit status: 0 decided (elementary/exhausted), 2 invalid input, 3 unknown.
Quote expressions; write multiplication as `*` and powers as `**`.

## The 0.1 contract is still available

```python
from integral_compass.classic import integrate as classic_integrate
assert classic_integrate("exp(-x**2)") is None  # Risch-proven non-elementarity
```

Classic unknown cases raise `IntegrationUndeterminedError`. Use `--classic` on the
CLI. Its `None` has a different meaning from the depth-search API. The variable is
now keyword-only in the new API: `integrate(expr, 3, variable=t)`.

## Limits and verification

Single-variable symbolic expressions only; no arbitrary callables or free parameters.
Strings use a real variable. Inputs use a restricted AST parser, not `eval`.
The classroom rational path caps polynomial degree at 30. Unsupported absolute-value,
piecewise, algebraic-root representation and cyclic-equation cases remain unknown.
A computation deadline does not establish mathematical non-integrability.

Answers are local identities away from singularities and branch boundaries; the
package does not compute maximal domains. For real rational logarithms, derivative
verification uses `(log|g|)'=g'/g` where g is nonzero. The returned expression omits C.

## Develop and collaborate

```bash
python -m pip install -e '.[dev]'
python -m pytest
ruff check .
python -m build
python -m twine check dist/*
```

[CONTRIBUTING.md](CONTRIBUTING.md) explains genuine team contributions.
[Publishing](docs/releasing.md) is prepared but not enabled by a PyPI account binding.
The package and documentation were developed with OpenAI Codex assistance; contributors
should review and understand submitted code. Algorithms are standard mathematics;
[SymPy](https://www.sympy.org/) is the symbolic backend. MIT licensed.
