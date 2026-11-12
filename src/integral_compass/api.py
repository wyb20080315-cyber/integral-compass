"""Public depth-controlled API and bounded worker transport."""

import json
import math
import subprocess
import sys
import time
from dataclasses import replace
from typing import Literal

import sympy as sp

from .models import IntegrationResult, Step
from .parser import make_symbol, parse_expression


def _analyze(expression, variable, *, timeout, depth=None, mode="search"):
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not (
            math.isfinite(timeout) and timeout > 0):
        raise ValueError("timeout must be a finite positive number of seconds")
    if depth is not None and (type(depth) is not int or depth < 1):
        raise ValueError("depth must be None or a positive integer; the root is depth 1")
    x = make_symbol(variable)
    f = parse_expression(expression, x)
    payload = {"expression": str(f), "variable": x.name, "assumptions": x.assumptions0,
               "depth": depth, "mode": mode}

    def unknown(method, reason):
        return IntegrationResult("unknown", f, x, method=method, reason=reason,
                                 search_depth=depth)

    try:
        process = subprocess.run(
            [sys.executable, "-m", "integral_compass._worker"],
            input=json.dumps(payload), text=True, capture_output=True, timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return unknown("timeout", f"Computation exceeded {timeout:g} seconds; the search "
                       "was not completed. A timeout is unknown, never an exhausted search.")
    if process.returncode != 0:
        return unknown("backend_error", "The integration worker failed; the search was not completed.")
    try:
        data = json.loads(process.stdout)
        primitive = (parse_expression(data["antiderivative"], x)
                     if data["antiderivative"] is not None else None)
        return IntegrationResult(
            status=data["status"], integrand=f, variable=x, antiderivative=primitive,
            method=data["method"], verified=data["verified"], reason=data["reason"],
            steps=tuple(Step(s["title"], s["explanation"], s["expression"], tuple(s["rows"]))
                        for s in data["steps"]),
            search_depth=data["search_depth"], depth_reached=data["depth_reached"],
            nodes_visited=data["nodes_visited"], search_complete=data["search_complete"],
            search_tree=tuple(data["search_tree"]),
        )
    except (KeyError, TypeError, ValueError):
        return unknown("backend_error", "The worker returned an unsupported result.")


def analyze(expression: str | sp.Expr, depth: int | None = None, *,
            variable: str | sp.Symbol = "x", timeout: float | None = None) -> IntegrationResult:
    """Use auto Risch+search when depth is None, otherwise bounded search only.

    The root is level 1. None imposes no depth limit. Auto mode has a shared
    time budget (10 seconds by default): 30% for Risch, the remainder for step search.
    """
    if depth is not None:
        return _analyze(expression, variable, timeout=10.0 if timeout is None else timeout,
                        depth=depth)
    budget = 10.0 if timeout is None else timeout
    if isinstance(budget, bool) or not isinstance(budget, (int, float)) or not (
            math.isfinite(budget) and budget > 0):
        raise ValueError("timeout must be a finite positive number of seconds")
    started = time.monotonic()
    precheck = _analyze(expression, variable, timeout=budget * 0.3, mode="risch")
    if precheck.status == "non_elementary":
        return precheck
    remaining = budget - (time.monotonic() - started)
    search = (_analyze(expression, variable, timeout=remaining) if remaining > 0 else
              replace(precheck, status="unknown", antiderivative=None, method="timeout",
                      verified=False, reason="The total time budget was exhausted before step search."))
    if search.status == "elementary":
        note = Step("Automatic Risch precheck", "Risch precheck: " + precheck.status +
                    ". The derivation below was found by the classroom search.")
        return replace(search, steps=(note, *search.steps))
    if precheck.status == "elementary":
        return replace(
            precheck, method="risch_fallback", search_tree=search.search_tree,
            depth_reached=search.depth_reached, nodes_visited=search.nodes_visited,
            reason="Risch supplied a verified elementary primitive; the classroom search "
                   f"did not produce a path ({search.method}).",
            steps=precheck.steps + (Step("Classroom search", search.reason),))
    return replace(search, steps=(Step("Automatic Risch precheck", precheck.reason), *search.steps))


def integrate(expression: str | sp.Expr, depth: int | None = None, *,
              variable: str | sp.Symbol = "x", timeout: float | None = None,
              show_steps: bool = True) -> sp.Expr | Literal["unknown"] | None:
    """Return a primitive, 'unknown', or None; inspect analyze().status for why None.

    A successful call prints its actual solution path unless show_steps=False.
    None means exhausted for a bounded search, or Risch-proven non-elementarity
    in automatic mode. Unknown means no decision, never a proof of impossibility.
    """
    return IntegralSolver(expression, depth, variable=variable, timeout=timeout).solve(
        show_steps=show_steps)


class IntegralSolver:
    """Keep a problem, cache its result, and display its solution or search tree."""

    def __init__(self, expression: str | sp.Expr, depth: int | None = None, *,
                 variable: str | sp.Symbol = "x", timeout: float | None = None):
        self.expression = expression
        self.depth = depth
        self.variable = variable
        self.timeout = timeout
        self.result: IntegrationResult | None = None

    def analyze(self) -> IntegrationResult:
        settings = (self.expression, self.depth, self.variable, self.timeout,
                    type(self.depth), type(self.timeout))
        if self.result is None or settings != getattr(self, "_settings", None):
            self.result = analyze(self.expression, self.depth, variable=self.variable,
                                  timeout=self.timeout)
            self._settings = settings
        return self.result

    def solve(self, *, show_steps: bool = True) -> sp.Expr | Literal["unknown"] | None:
        result = self.analyze()
        if result.status == "elementary":
            if show_steps:
                self.show()
            return result.antiderivative
        if result.status in ("exhausted", "non_elementary"):
            return None
        return "unknown"

    def show(self) -> None:
        print(self.analyze().explain())

    def show_tree(self) -> None:
        result = self.analyze()
        for node in result.search_tree:
            print(f"node {node['id']} | parent={node['parent']} | depth={node['depth']} | "
                  f"{node['integrand']} | {node['status']}")
            if "u" in node:
                print(f"  D: {node['u']} | I: {node['dv']} -> {node.get('v', '?')}")
