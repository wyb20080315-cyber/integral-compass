"""Two-direction integration-by-parts search with rational leaves.

No generic integrate()/Risch fallback may bypass the requested depth. A side
primitive must come from explicit terminal rules before applying parts.
"""

from dataclasses import dataclass
from itertools import count

import sympy as sp

from .engine import _elementary, _rational, _verified
from .models import IntegrationResult, Step
from .parser import ExpressionError, parse_expression


@dataclass
class _Outcome:
    status: str
    primitive: sp.Expr | None = None
    steps: tuple[Step, ...] = ()


class _Search:
    def __init__(self, x, limit, unlimited=False):
        self.x = x
        self.limit = limit
        self.unlimited = unlimited
        self.tree = []
        self.frontier = 0
        self.direct_cache = {}

    def direct(self, f):
        if f in self.direct_cache:
            return self.direct_cache[f]
        x = self.x
        answer = None
        if f.is_polynomial(x) and sp.degree(f, x) <= 30:
            primitive = sp.Poly(f, x).integrate().as_expr()
            answer = _Outcome("elementary", primitive, (
                Step("Power rule", "Integrate the polynomial term by term.", str(primitive)),))
        elif f.is_rational_function(x):
            rational = _rational(f, x)
            if rational is not None:
                answer = _Outcome("elementary", rational[0], tuple(rational[1]))
        else:
            coefficient, body = f.as_independent(x, as_Add=False)
            if body.func in (sp.exp, sp.sin, sp.cos):
                slope = sp.diff(body.args[0], x)
                if slope != 0 and not slope.has(x):
                    if body.func == sp.exp:
                        primitive = body / slope
                    elif body.func == sp.sin:
                        primitive = -sp.cos(body.args[0]) / slope
                    else:
                        primitive = sp.sin(body.args[0]) / slope
                    answer = _Outcome("elementary", coefficient * primitive, (
                        Step("Basic integral", "Use a linear-inner-function table rule.",
                             f"Integral of {f} = {coefficient * primitive}"),))
            elif body.is_Pow and body.exp.is_Rational and body.exp != -1:
                slope = sp.diff(body.base, x)
                if slope != 0 and not slope.has(x):
                    primitive = coefficient * body.base**(body.exp + 1) / (slope * (body.exp + 1))
                    answer = _Outcome("elementary", primitive, (
                        Step("Power rule", "Integrate an affine base to a rational power.",
                             str(primitive)),))
        if answer is not None and not _verified(answer.primitive, f, x):
            answer = None
        self.direct_cache[f] = answer
        return answer

    @staticmethod
    def splits(body):
        factors = sp.Mul.make_args(body)
        if len(factors) == 1:
            yield body, sp.S.One
            yield sp.S.One, body
            return
        # Enumerate every factor bipartition once, then try both directions.
        for mask in range((1 << (len(factors) - 1)) - 1):
            left, right = [factors[0]], []
            for index, factor in enumerate(factors[1:]):
                (left if mask & (1 << index) else right).append(factor)
            u, dv = sp.Mul(*left), sp.Mul(*right)
            yield u, dv
            yield dv, u

    def visit(self, f, depth=1, parent=None, ancestors=frozenset(), decision=None,
              origin=None, context=None):
        node = {"id": len(self.tree), "parent": parent, "depth": depth,
                "integrand": str(f), "status": "searching"}
        if decision:
            node.update(decision)
        self.tree.append(node)

        def finish(outcome):
            node["status"] = outcome.status
            return outcome

        if origin is None:
            origin, context = f, (sp.S.Zero, sp.S.One)
        elif origin != 0:
            ratio = sp.simplify(sp.trigsimp(sp.cancel(f / origin)))
            if ratio != 0 and not ratio.has(self.x) and ratio.is_finite is True:
                # Carry the entire path as J = A + B*integral(current).
                # If current = k*origin, solve (1-B*k)*J = A.
                a, b = context
                multiplier = sp.simplify(b * ratio)
                denominator = sp.simplify(1 - multiplier)
                node["cycle_ratio"] = str(ratio)
                node["equation"] = f"J = ({a}) + ({multiplier})*J"
                if denominator == 0:
                    node["reason"] = "Degenerate cycle: no independent equation for J."
                    return finish(_Outcome("unknown" if self.unlimited else "exhausted"))
                if denominator.is_zero is False:
                    root_primitive = sp.factor_terms(a / denominator)
                    if _verified(root_primitive, origin, self.x):
                        return finish(_Outcome("elementary", ratio * root_primitive, (
                            Step("Cycle detected", "The remaining integrand is a constant "
                                 "multiple of this subproblem's original integrand.", str(f)),
                            Step("Solve cycle equation", node["equation"] +
                                 f"; divide by {denominator}.", str(root_primitive)),)))
                node["reason"] = "Cycle equation could not be solved and verified."
                return finish(_Outcome("unknown"))

        direct = self.direct(f)
        if direct is not None:
            return finish(direct)
        if f.has(sp.Abs):
            node["reason"] = "Piecewise/absolute-value search rules are not implemented."
            return finish(_Outcome("unknown"))
        coefficient, body = f.as_independent(self.x, as_Add=False)
        if self.unlimited and body in ancestors:
            node["reason"] = "An ancestor cycle outside the current origin remains unresolved."
            return finish(_Outcome("unknown"))
        ancestors = ancestors | {body}
        if f.is_Add:
            # Each summand is a separate integration problem with its own J.
            parts = [self.visit(term, depth, node["id"])
                     for term in sp.Add.make_args(f)]
            if all(part.status == "elementary" for part in parts):
                return finish(_Outcome("elementary", sum(p.primitive for p in parts), (
                    Step("Linearity", "Integrate each summand; linearity does not consume "
                         "an integration-by-parts level."),
                    *(step for part in parts for step in part.steps))))
            return finish(_Outcome("unknown" if any(p.status == "unknown" for p in parts)
                                   else "exhausted"))
        if f.is_rational_function(self.x):
            node["reason"] = "Rational terminal exceeded the supported degree or output representation."
            return finish(_Outcome("unknown"))
        if depth >= self.limit:
            self.frontier += 1
            node["reason"] = "Depth boundary reached without a terminal rule."
            return finish(_Outcome("exhausted"))
        if len(sp.Mul.make_args(body)) > 8:
            node["reason"] = "More than 8 product factors; partition search is unsupported."
            return finish(_Outcome("unknown"))
        uncertain = False
        for u, dv in self.splits(body):
            side = self.direct(dv)
            if side is None:
                self.tree.append({"id": len(self.tree), "parent": node["id"],
                                  "depth": depth + 1, "integrand": str(dv),
                                  "status": "unknown", "u": str(u), "dv": str(dv),
                                  "reason": "The side primitive v is unavailable in the basic rules."})
                uncertain = True
                continue
            v = side.primitive
            du = sp.diff(u, self.x)
            remainder = sp.factor_terms(du * v)
            child = self.visit(remainder, depth + 1, node["id"], ancestors,
                               {"u": str(u), "dv": str(dv), "v": str(v)},
                               origin=origin,
                               context=(context[0] + context[1]*coefficient*u*v,
                                        -context[1]*coefficient))
            if child.status == "elementary":
                primitive = sp.factor_terms(coefficient * (u * v - child.primitive))
                step = Step("DI / integration by parts", f"At depth {depth}: choose D={u}, "
                            f"I={dv}, keeping the constant multiplier {coefficient}. "
                            "Use integral(c*u*dv) = c*(u*v - integral(v*du)).", rows=(
                                {"constant multiplier": str(coefficient),
                                 "D (u)": str(u), "D derivative (du/dx)": str(du),
                                 "I (dv/dx)": str(dv), "I primitive (v)": str(v),
                                 "remaining integrand": str(remainder)},))
                return finish(_Outcome("elementary", primitive, (
                    step, Step("Integrate the I side", "Obtain v using terminal rules."),
                    *side.steps, *child.steps,
                    Step("Recombine", f"Return from depth {depth + 1} to depth {depth}.",
                         str(primitive)))))
            uncertain |= child.status == "unknown"
        return finish(_Outcome("unknown" if uncertain else "exhausted"))


def search_core(f, x, depth):
    # Iterative deepening is fair between directions. There is no hidden level
    # cap for None; the outer worker deadline bounds elapsed time instead.
    total = 0
    cache = {}
    for limit in count(1) if depth is None else (depth,):
        search = _Search(x, limit, unlimited=depth is None)
        search.direct_cache = cache
        outcome = search.visit(f)
        total += len(search.tree)
        reached = max(node["depth"] for node in search.tree)
        primitive = outcome.primitive
        invalid_answer = False
        if outcome.status == "elementary":
            try:
                valid = _elementary(primitive) and _verified(primitive, f, x)
                parse_expression(str(primitive), x)
            except ExpressionError:
                valid = False
            if valid:
                return IntegrationResult(
                    "elementary", f, x, primitive, "parts_search", True,
                    "Verified locally away from singularities and branch boundaries; add C.",
                    outcome.steps + (Step("Derivative check", "Simplify F'(x) - f(x).", "0"),),
                    depth, reached, total, False, tuple(search.tree))
            outcome = _Outcome("unknown")
            invalid_answer = True
        if depth is not None or search.frontier == 0 or invalid_answer:
            exhausted = outcome.status == "exhausted"
            return IntegrationResult(
                outcome.status, f, x, method="parts_search",
                reason=("Every generated branch within the requested depth was exhausted. "
                        "This is a search limit, not proof of a non-elementary integral."
                        if exhausted else "At least one branch could not be evaluated with the "
                        "available rules; the search is unknown."),
                search_depth=depth, depth_reached=reached, nodes_visited=total,
                search_complete=exhausted, search_tree=tuple(search.tree))
    raise AssertionError("unreachable")
