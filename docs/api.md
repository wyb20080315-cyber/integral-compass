# API reference

## `analyze(expression, variable="x", *, timeout=10.0)`

Accept a string or SymPy `Expr`. `variable` is a name (real by default) or a SymPy
`Symbol`. Pass the expression's own Symbol when supplying symbolic input.
Parameters other than the integration variable are unsupported.

Allowed functions: `sin`, `cos`, `tan`, `cot`, `sec`, `csc`, `asin`, `acos`, `atan`,
`exp`, `log`, `sqrt`, `Abs`. Each takes one argument. Constants: `pi`, `E`, `I`.
Allowed operations: `+ - * / **` and parentheses. Decimal literals are read as
exact rationals. Accepting an expression is not a guarantee of solving it.

Returns frozen `IntegrationResult`:

| Field | Meaning |
| --- | --- |
| `status` | `elementary`, `non_elementary`, or `unknown` |
| `integrand`, `variable` | Normalized SymPy input and integration symbol |
| `antiderivative` | SymPy expression for elementary success; otherwise `None` |
| `method` | `polynomial`, `di`, `partial_fractions`, `risch`, `sympy_fallback`, `unsupported`, `timeout`, or `backend_error` |
| `verified` | True only for a verified elementary result |
| `reason` | Interpretation or limitation |
| `steps` | Tuple of `Step(title, explanation, expression, rows)` |

`to_dict()` returns JSON-compatible data (expressions become strings).
`explain()` renders a human-readable English explanation; Chinese guidance is in
the user guide. Step expressions are display strings, not executable Python.

The deadline applies to the worker, including startup, algebra and verification;
the bounded input parser runs before that deadline. No explicit RAM limit is
enforced. A killed/failed worker produces `unknown`, not `non_elementary`.

## `integrate(expression, variable="x", *, timeout=10.0)`

Returns a SymPy expression (without `C`) for elementary success. Returns `None`
only for proven non-elementarity. Unknown raises `IntegrationUndeterminedError`,
whose `.result` contains the full result. Invalid inputs raise `ExpressionError`
(a `ValueError` subclass); invalid timeouts raise `ValueError`.

## CLI

`integral-compass EXPRESSION [--variable x] [--timeout 10] [--json]`.
Equivalent: `python -m integral_compass`.
Exit status: 0 decided, 2 invalid input, 3 unknown.

## Stability

Version 0.1 is an educational alpha. Expressions and method routing may change
with SymPy versions; prefer comparing derivatives over exact output strings.
This release supports SymPy 1.13 and 1.14 and Python 3.10+.
