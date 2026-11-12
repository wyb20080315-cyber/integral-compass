# API reference — 0.4

## `integrate(expression, depth=None, *, variable="x", timeout=None, show_steps=True)`

Return a SymPy primitive, Python `None` for an exhausted bounded search, the string
`"None, verified by Risch"` for certified non-elementarity in automatic mode, or
`"unknown, REASON: explanation"` for an unresolved computation. Successful calls automatically
print the solution path. Set `show_steps=False` for silent operation. The arbitrary
constant C is omitted from the expression and included in the printed explanation.

`depth` must be a positive Python int or None. The original problem is level 1,
so depth 3 permits at most two integration-by-parts decisions along a path.
None applies no depth cap and enables automatic Risch+search. `timeout=None` means
a shared 10-second budget; an explicit positive timeout changes that budget. Risch
uses at most 30%, then search gets the remaining time. A Risch proof can end the
computation immediately; a verified Risch primitive is retained as a fallback.
With a finite depth, Risch does not bypass the bound and timeout defaults to 10 seconds.

`variable` is keyword-only, a name (real by default) or a SymPy Symbol. When passing
an existing symbolic expression, pass its own Symbol to preserve assumptions.

## `analyze(expression, depth=None, *, variable="x", timeout=None)`

Same computation, without printing; returns `IntegrationResult`:

| Field | Meaning |
| --- | --- |
| `status` | `elementary`, `exhausted`, `non_elementary`, or `unknown` |
| `integrand`, `variable` | Normalized SymPy input |
| `antiderivative` | Expression for success, otherwise None; inspect status to distinguish failures |
| `method`, `verified`, `reason` | Solver route, derivative check and interpretation |
| `reason_code` | Stable unknown category: timeout, unsupported_rule, unresolved_branch, backend_error, verification_failed |
| `value` | Public expression/None/explanatory string; JSON serializes expressions as strings |
| `steps` | Successful derivation as `Step(title, explanation, expression, rows)` |
| `search_depth` | Requested maximum, or None |
| `depth_reached` | Greatest level in the reported pass |
| `nodes_visited` | Node count, including earlier iterative-deepening passes |
| `search_complete` | True only for a fully exhausted bounded search |
| `search_tree` | Nodes with id, parent, depth, integrand, status and decision metadata |

`to_dict()` returns JSON-compatible data; `explain()` renders English text.
The tree describes the final search pass, including attempted side primitives.
A successful path may stop before exploring siblings; it does not need every branch.

## `IntegralSolver(expression, depth=None, *, variable="x", timeout=None)`

- `.analyze()` computes and caches the structured result, without printing.
- `.solve(show_steps=True)` returns an expression/None/an explanatory string and prints successful steps.
- `.show()` displays the cached/current result, including failure explanations.
- `.show_tree()` prints the explored final-pass tree.
- `.result` is None until the first computation, then the structured result.

Changing problem settings invalidates the cached computation.

## Input and errors

Allowed functions: sin, cos, tan, cot, sec, csc, asin, acos, atan, exp, log, sqrt,
Abs, each with one argument. Constants: pi, E, I. Operators: `+ - * / **`.
Accepting syntax does not guarantee a search rule exists for it. Decimal literals
are exact rationals. No extra free parameters, arbitrary Python callables or code.

Malformed inputs raise `ExpressionError` (a ValueError). Invalid depth/timeouts raise
ValueError. Timeouts/backend failures return unknown; they never mean exhausted.
The worker deadline includes startup and algebra, not the bounded parent-side parser.
No explicit RAM quota is enforced; this is a local educational tool, not a hardened service.

## Classic compatibility API

`integral_compass.classic.analyze(expr, variable="x", *, timeout=10)` and
`.integrate(...)` preserve the 0.1 Risch-based semantics: None only when a
NonElementaryIntegral remainder certifies non-elementarity, unknown raises
IntegrationUndeterminedError. This API does not accept a depth and does not
provide the new search contract. CLI: `--classic`, incompatible with `--depth`.

## Cycle equations

Before terminal/depth checks, compare the remainder to the current subproblem's
original integrand. For a constant multiple k, carry the existing path as
J=A+B*integral(current), then solve (1-B*k)*J=A. The solution must pass derivative
verification. A zero denominator is a degenerate route, never a primitive.
Linearity assigns each summand its own original integral and equation.

## Failure-message contract

Unknown strings start with `unknown, ` and include their cause. Prefer the stable
structured `reason_code` over parsing prose. Prefixes are `unknown, timeout:`,
`unknown, unsupported rule:`, `unknown, unresolved branches:`,
`unknown, backend error:`, and `unknown, verification failed:`.
Only a real Risch non-elementarity certificate produces the exact string
`None, verified by Risch`; not every default-mode call returns this string.
Successful default-mode calls still return primitive expressions.
The classic compatibility API retains Python None and exceptions as before.
