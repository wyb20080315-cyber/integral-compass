"""Public depth-controlled API and bounded worker transport."""

import json
import math
import subprocess
import sys
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
            variable: str | sp.Symbol = "x", timeout: float = 10.0) -> IntegrationResult:
    """Search both integration-by-parts directions; return a structured outcome.

    The root is level 1. None imposes no depth limit; the worker deadline still
    applies. This search uses classroom rules, not the classic Risch backend.
    """
    return _analyze(expression, variable, timeout=timeout, depth=depth)


def integrate(expression: str | sp.Expr, depth: int | None = None, *,
              variable: str | sp.Symbol = "x", timeout: float = 10.0,
              show_steps: bool = True) -> sp.Expr | Literal["unknown"] | None:
    """Return a primitive, 'unknown', or None for a fully exhausted bounded search.

    A successful call prints its actual solution path unless show_steps=False.
    None is relative to the supplied depth and rules, not a non-elementarity proof.
    """
    return IntegralSolver(expression, depth, variable=variable, timeout=timeout).solve(
        show_steps=show_steps)


class IntegralSolver:
    """Keep a problem, cache its result, and display its solution or search tree."""

    def __init__(self, expression: str | sp.Expr, depth: int | None = None, *,
                 variable: str | sp.Symbol = "x", timeout: float = 10.0):
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
        if result.status == "exhausted":
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
