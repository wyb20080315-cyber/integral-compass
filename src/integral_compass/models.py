"""Structured, serializable explanations for notebooks and the CLI."""

from dataclasses import dataclass, field
from typing import Literal

import sympy as sp

Status = Literal["elementary", "non_elementary", "exhausted", "unknown"]


@dataclass(frozen=True)
class Step:
    title: str
    explanation: str
    expression: str | None = None
    rows: tuple[dict, ...] = ()


@dataclass(frozen=True)
class IntegrationResult:
    status: Status
    integrand: sp.Expr
    variable: sp.Symbol
    antiderivative: sp.Expr | None = None
    method: str = "none"
    verified: bool = False
    reason: str = ""
    steps: tuple[Step, ...] = field(default_factory=tuple)

    search_depth: int | None = None
    depth_reached: int = 0
    nodes_visited: int = 0
    search_complete: bool = False
    search_tree: tuple[dict, ...] = ()
    reason_code: str = ""

    @property
    def value(self) -> sp.Expr | str | None:
        """The simple public value, including a reason for every unknown result."""
        if self.status == "elementary":
            return self.antiderivative
        if self.status == "non_elementary":
            return "None, verified by Risch"
        if self.status == "exhausted":
            return None
        code = self.reason_code or (self.method if self.method in ("timeout", "backend_error")
                                    else "unresolved_branch")
        labels = {"unsupported_rule": "unsupported rule", "unresolved_branch": "unresolved branches",
                  "backend_error": "backend error", "verification_failed": "verification failed"}
        return f"unknown, {labels.get(code, code)}: {self.reason}"

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "integrand": str(self.integrand),
            "variable": str(self.variable),
            "antiderivative": (str(self.antiderivative)
                               if self.antiderivative is not None else None),
            "method": self.method,
            "verified": self.verified,
            "reason": self.reason,
            "reason_code": self.reason_code,
            "value": str(self.value) if isinstance(self.value, sp.Expr) else self.value,
            "search_depth": self.search_depth,
            "depth_reached": self.depth_reached,
            "nodes_visited": self.nodes_visited,
            "search_complete": self.search_complete,
            "search_tree": list(self.search_tree),
            "steps": [{"title": s.title, "explanation": s.explanation,
                       "expression": s.expression, "rows": list(s.rows)} for s in self.steps],
        }

    def explain(self) -> str:
        lines = [f"Integral Compass | {self.status}", f"Input: {self.integrand}",
                 f"Method: {self.method}"]
        if self.depth_reached:
            limit = "unbounded" if self.search_depth is None else str(self.search_depth)
            lines.append(f"Depth limit: {limit} | Reached: {self.depth_reached} | "
                         f"Nodes visited: {self.nodes_visited}")
        for index, step in enumerate(self.steps, 1):
            lines.extend([f"{index}. {step.title}", f"   {step.explanation}"])
            if step.expression is not None:
                lines.append(f"   {step.expression}")
            for row in step.rows:
                lines.append("   " + " | ".join(f"{key}={value}" for key, value in row.items()))
        if self.antiderivative is not None:
            lines.append(f"F({self.variable}) = {self.antiderivative} + C")
        else:
            lines.append(f"Return value: {self.value!r}")
        lines.append(f"Verified: {self.verified}")
        lines.append(self.reason)
        return "\n".join(lines)


class IntegrationUndeterminedError(RuntimeError):
    """Raised instead of None when no elementary-integrability decision was made."""

    def __init__(self, result: IntegrationResult):
        self.result = result
        super().__init__(result.reason)
