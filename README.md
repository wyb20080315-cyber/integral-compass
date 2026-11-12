# Integral Compass 🧭

**Follow the steps. Check the derivative. Know when the answer is unknown.**

An educational Python package inspired by first-year calculus notes: DI (tabular
integration by parts), partial fractions, and the question “does an elementary
antiderivative exist?” It returns a verified elementary expression, `None` **only
when SymPy's Risch backend proves non-elementarity**, or an explicit unknown outcome.

[中文完整指南](docs/guide.zh-CN.md) · [Mathematics and limits](docs/mathematics.md) ·
[API](docs/api.md) · [60-second demo](docs/demo.zh-CN.md) · [Publishing](docs/releasing.md)

## Why build this?

A calculator's final expression often hides the useful lesson: which factor was
differentiated, why a repeated denominator needs several fractions, or whether an
unevaluated integral means a mathematical impossibility or a software limitation.
Integral Compass makes these distinctions inspectable in a small Python API and CLI.

Our contribution is the classroom strategy layer, structured explanations, derivative
verification, bounded execution and three-outcome API. SymPy supplies symbolic algebra,
partial-fraction decomposition, rational-term integration and the existing Risch backend.
**We do not claim to have invented DI, partial fractions, or Risch, or to implement a
complete Risch algorithm.**

## Install

Requires Python 3.10 or newer. From a source checkout:

```bash
git clone https://github.com/wyb20080315-cyber/integral-compass.git
cd integral-compass
python -m venv .venv
# macOS / Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install .
```

After version 0.1.0 has been published to PyPI, the index installation will be:

```bash
python -m pip install integral-compass
```

The presence of this command in the documentation is not a claim that publication
has already completed. See [release instructions](docs/releasing.md) for verification.

## Try it

```python
from integral_compass import analyze, integrate, IntegrationUndeterminedError

result = analyze("x**2 * exp(x)")
print(result.explain())       # DI rows, primitive and derivative check
print(result.antiderivative)  # (x**2 - 2*x + 2)*exp(x)
assert result.verified

fraction = analyze("1/((x+1)*(x**2+1)**2)")
print(fraction.explain())     # repeated quadratic partial fractions

assert integrate("exp(-x**2)") is None  # proven non-elementary, not nonexistent

try:
    integrate("Abs(x)")      # piecewise primitives are outside this first release
except IntegrationUndeterminedError as error:
    print(error.result.status)  # unknown; never silently converted to None
```

The returned expression omits the arbitrary constant `C`; the text explanation includes it.

```bash
integral-compass 'x**2 * exp(x)'
integral-compass '1/((x+1)*(x**2+1)**2)' --json
python -m integral_compass 'exp(-x**2)'
python examples/demo.py
```

## Three outcomes

| `analyze(...).status` | Meaning | `integrate(...)` |
| --- | --- | --- |
| `elementary` | An elementary expression passed symbolic derivative verification | SymPy expression |
| `non_elementary` | The Risch backend returned a certified non-elementary remainder | `None` |
| `unknown` | Unsupported case, unresolved verification, backend failure or timeout | `IntegrationUndeterminedError` |

An ordinary unevaluated SymPy `Integral` is **not** evidence of non-elementarity.
For example, `exp(-x**2)` has an antiderivative expressible using `erf`, but not using
elementary functions. This package concerns **indefinite elementary integration**,
not definite integrals, numerical quadrature, or convergence.

## Supported scope

- Univariate expressions; no free symbolic parameters or arbitrary Python callables.
- Polynomials; DI for a polynomial times `exp(a*x+b)`, `sin(a*x+b)` or `cos(a*x+b)`.
- Rational functions with polynomial division and partial fractions, including repeated
  linear and quadratic factors. Classroom paths cap polynomial degree at 30.
- Additional verified elementary cases through SymPy; only DI and rational paths promise
  classroom explanations. The exponential/logarithmic Risch implementation is incomplete.
- Strings use a real integration variable. Expressions use `*`, `**`, rational literals,
  `pi`, `E`, `I`, and the functions listed in the [API](docs/api.md).
- Answers are local identities away from poles and branch boundaries. We do not compute
  maximal domains or claim global continuity across singularities.

The expression parser uses a restricted Python AST, not `eval` or string `sympify`.
Input size and numeric exponents are bounded. Symbolic integration and verification run
in a child process with a default 10-second deadline. These controls are for a local
educational tool; they do not make it a hardened public computation service.

## Develop and contribute

```bash
python -m pip install -e '.[dev]'
python -m pytest
ruff check .
python -m build
python -m twine check dist/*
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for team tasks, real Git contributions, AI-use
disclosure and review expectations. CI tests Python 3.10–3.13 on Linux and 3.12 on Windows,
builds a wheel and sdist, and smoke-tests the installed wheel outside the source tree.

## Credits

Motivated by the project proposer's personal calculus notes. Algorithms are standard
mathematics; [SymPy](https://www.sympy.org/) is the symbolic backend. The package and
documentation were developed with OpenAI Codex assistance. Contributors should review
and understand the code they submit. This project is distributed under the MIT license.
