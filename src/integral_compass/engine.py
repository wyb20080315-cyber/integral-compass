"""Classroom strategies plus a restricted SymPy Risch decision backend."""

import sympy as sp
from sympy.integrals.risch import NonElementaryIntegral, risch_integrate

from .models import IntegrationResult, Step
from .parser import FUNCTIONS, parse_expression


def _verified(primitive, integrand, variable):
    # This is a local identity on intervals where real log arguments are nonzero.
    # Rewriting log|g| avoids a spurious unresolved case at the excluded point g=0.
    primitive = primitive.replace(
        lambda e: e.func == sp.log and e.args[0].func == sp.Abs
        and e.args[0].args[0].is_real is True,
        lambda e: sp.log(e.args[0].args[0]),
    )
    residual = sp.diff(primitive, variable) - integrand
    return sp.simplify(sp.trigsimp(residual)) == 0


def _real_logs(primitive, variable):
    # On real intervals excluding zeros, d(log|g|)/dx = g'/g.
    if variable.is_real:
        return primitive.replace(
            lambda e: e.func == sp.log and e.args[0].is_real is True,
            lambda e: sp.log(sp.Abs(e.args[0])),
        )
    return primitive


def _elementary(primitive):
    return not primitive.has(sp.Integral, sp.Derivative, sp.Piecewise, sp.RootSum) and all(
        function.func in set(FUNCTIONS.values())
        for function in primitive.atoms(sp.Function)
    )


def _di(f, x):
    factors = sp.Mul.make_args(f)
    candidates = [g for g in factors if g.func in (sp.exp, sp.sin, sp.cos)]
    if len(candidates) != 1:
        return None
    g = candidates[0]
    p = sp.cancel(f / g)
    if not p.is_polynomial(x):
        return None
    degree = sp.degree(p, x)
    if degree > 30:
        return None
    slope = sp.diff(g.args[0], x)
    if slope == 0 or slope.has(x):
        return None
    derivative = p
    basis, coefficient = g, sp.S.One
    terms, rows = [], []
    for i in range(int(degree) + 1):
        # Work with a separate basis and coefficient to avoid generic integrate calls.
        if basis.func == sp.exp:
            coefficient /= slope
        elif basis.func == sp.sin:
            basis = sp.cos(basis.args[0])
            coefficient *= -1 / slope
        else:
            basis = sp.sin(basis.args[0])
            coefficient /= slope
        integral = coefficient * basis
        terms.append((-1)**i * derivative * integral)
        rows.append({"sign": "+" if i % 2 == 0 else "-", "D": str(derivative),
                     "I": str(integral)})
        derivative = sp.diff(derivative, x)
    rows.append({"sign": "stop", "D": "0", "I": "remainder vanishes"})
    answer = sp.simplify(sum(terms))
    return answer, [Step("DI table", "Differentiate the polynomial to zero; repeatedly integrate "
                        "the exponential or trigonometric factor. Sum signed diagonal products.",
                        rows=tuple(rows))]


def _rational(f, x):
    numerator, denominator = sp.fraction(sp.cancel(f))
    if max(sp.degree(numerator, x), sp.degree(denominator, x)) > 30:
        return None
    quotient, remainder = sp.div(numerator, denominator, x)
    steps = [Step("Polynomial division", "Separate the polynomial part from the proper fraction.",
                  str(quotient + remainder / denominator))]
    decomposition = sp.apart(remainder / denominator, x)
    steps.append(Step("Partial fractions", "Split over irreducible factors. Repeated factors "
                      "need a term for every power; quadratic factors may need linear numerators.",
                      str(decomposition)))
    terms = sp.Add.make_args(quotient + decomposition)
    primitives = []
    for term in terms:
        primitive = _real_logs(sp.integrate(term, x, risch=True), x)
        if not _elementary(primitive):
            return None
        primitives.append(primitive)
        steps.append(Step("Integrate one term", f"Integral of {term}", str(primitive)))
    return sp.Add(*primitives), steps


def analyze_core(f, x):
    steps = []

    def solved(candidate, method, explanation):
        if not _elementary(candidate):
            return None
        # The public expression grammar also bounds which outputs are supported.
        try:
            parse_expression(str(candidate), x)
        except ValueError:
            return None
        if not _verified(candidate, f, x):
            return None
        return IntegrationResult(
            "elementary", f, x, candidate, method, True,
            "Derivative verified symbolically. Valid locally away from singularities and "
            "branch boundaries; an arbitrary constant C is omitted from the returned expression.",
            tuple(explanation) + (Step("Derivative check", "Simplify F'(x) - f(x).", "0"),),
        )

    if f.is_polynomial(x) and sp.degree(f, x) <= 30:
        result = solved(sp.Poly(f, x).integrate().as_expr(), "polynomial",
                        [Step("Power rule", "Integrate each polynomial term.")])
        if result:
            return result
    di = _di(f, x)
    if di is not None:
        result = solved(di[0], "di", di[1])
        if result:
            return result
    if f.is_rational_function(x):
        rational = _rational(f, x)
        if rational is not None:
            result = solved(rational[0], "partial_fractions", rational[1])
            if result:
                return result

    # Do not infer non-elementarity from a generic unevaluated Integral.
    try:
        elementary_part, remainder = risch_integrate(f, x, separate_integral=True)
        if isinstance(remainder, NonElementaryIntegral):
            return IntegrationResult(
                "non_elementary", f, x, method="risch",
                reason="SymPy's Risch backend proved a non-elementary remainder. "
                       "This does not mean that a primitive or a numerical integral does not exist.",
                steps=(Step("Risch decision", "A certified non-elementary remainder remains.",
                            str(remainder)),),
            )
        if remainder == 0:
            # Keep nested logarithms intact: changing an inner log to log|g|
            # can alter the input's complex continuation outside its real domain.
            result = solved(elementary_part, "risch",
                            [Step("Risch backend", "Use SymPy's supported exponential/logarithmic "
                                  "integration algorithm.", str(elementary_part))])
            if result:
                return result
    except (NotImplementedError, ValueError, TypeError, KeyError, PolynomialError):
        steps.append(Step("Risch limitation", "The backend did not decide this expression."))

    # Success here is accepted only for elementary expressions with an exact derivative check.
    candidate = sp.integrate(f, x)
    result = solved(candidate, "sympy_fallback", steps + [
        Step("SymPy fallback", "Try additional integration methods. Classroom steps are not "
             "available for this fallback.", str(candidate))])
    if result:
        return result
    return IntegrationResult(
        "unknown", f, x, method="unsupported", reason="No verified elementary answer or "
        "Risch non-elementarity decision was obtained. This is not proof of non-elementarity.",
        steps=tuple(steps),
    )


PolynomialError = sp.polys.polyerrors.PolynomialError
