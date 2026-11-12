# Search mathematics and limits

## Integration-by-parts decisions

For an integrand `c*u*g`, use a terminal-rule primitive `v` of g and recurse on
`u'*v`. Recombine as `c*(u*v - integral(u'*v))`. Try both orientations of every
factor bipartition. The constant c is preserved. Sums are integrated by linearity;
they create independent obligations without adding a parts-decision level.

The root is level 1. Each integration-by-parts edge consumes one further level.
A terminal primitive may be accepted at the exact requested boundary. No general
integrator or Risch answer may shortcut that boundary in search mode.
A helper side primitive is obtained using terminal rules; it is not a free recursive
integration of an arbitrary factor. If unavailable, that direction remains unknown.

## Terminal rules

- Polynomial power rule (degree at most 30).
- Rational functions: polynomial division, SymPy `apart`, and integration of terms.
- Linear-argument exp, sin, cos with the correct slope multiplier.
- Rational powers of an affine base.

Repeated linear denominator factors need every power with constant numerators;
repeated irreducible quadratics need linear numerators for every power.
High-degree irreducible representations may be outside the supported output grammar.
Only rational-term integration uses the backend integrator in search mode.

## Complete relative to a grammar

With two canonical factors there are two directions. For more factors enumerate
all nonempty bipartitions and both orientations, up to eight canonical factors.
For a single factor, allow the implicit factor 1. This is not an exhaustive search
of every possible algebraic rewriting, introduced factor, substitution or identity.

For a specified depth, `exhausted` means all generated directions failed at or before
that boundary and none remained unknown. Its public value is None. This is an
algorithmic search outcome, not mathematical non-elementarity. For instance,
`x**2*exp(x)` is exhausted at depth 2 and solved at depth 3.

Unknown branches do not prevent trying siblings. A success wins; otherwise an
unresolved branch makes the result unknown. Timeouts and worker failures are unknown.
With no depth cap, iterative deepening fairly explores increasing finite depths.
Repeated states in an ancestor chain are marked unknown in unlimited mode; solving
cyclic integral equations is not implemented. Bounded search explores them up to its
boundary instead. A finite time budget still applies.

## Derivative verification and domains

A success must simplify `F' - f` to zero. For real rational logarithms,
`(log|g|)'=g'/g` is checked locally where real g is nonzero. Singular points and
branch boundaries are excluded; maximal domains are not computed. The API omits C.
Steps show the successful path; the search tree also records failed attempts.

## Classic Risch API

The independent `integral_compass.classic` module retains the original contract.
It uses SymPy's `risch_integrate(..., separate_integral=True)` and only treats a
`NonElementaryIntegral` remainder as evidence of non-elementarity. An ordinary
unevaluated Integral is not such evidence. Its None means proven non-elementarity;
unknown raises IntegrationUndeterminedError. SymPy's Risch implementation is incomplete,
especially outside exponential/logarithmic transcendental extensions.

References: [SymPy integrals](https://docs.sympy.org/latest/modules/integrals/integrals.html),
[partial fractions](https://docs.sympy.org/latest/modules/polys/reference.html#sympy.polys.partfrac.apart),
[Risch implementation](https://github.com/sympy/sympy/blob/master/sympy/integrals/risch.py).
The project proposer's calculus notes inspired the teaching flow. The project does
not claim a new mathematical algorithm or a complete implementation of Risch.
