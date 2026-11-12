"""Structured, serializable explanations for notebooks and the CLI."""

from dataclasses import dataclass, field
from typing import Literal

import sympy as sp

Status = Literal["elementary", "non_elementary", "unknown"]


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
            "steps": [{"title": s.title, "explanation": s.explanation,
                       "expression": s.expression, "rows": list(s.rows)} for s in self.steps],
        }

    def explain(self) -> str:
        lines = [f"Integral Compass | {self.status}", f"Input: {self.integrand}",
                 f"Method: {self.method}"]
        for index, step in enumerate(self.steps, 1):
            lines.extend([f"{index}. {step.title}", f"   {step.explanation}"])
            if step.expression is not None:
                lines.append(f"   {step.expression}")
            for row in step.rows:
                lines.append("   " + " | ".join(f"{key}={value}" for key, value in row.items()))
        if self.antiderivative is not None:
            lines.append(f"F({self.variable}) = {self.antiderivative} + C")
        lines.append(f"Verified: {self.verified}")
        lines.append(self.reason)
        return "\n".join(lines)


class IntegrationUndeterminedError(RuntimeError):
    """Raised instead of None when no elementary-integrability decision was made."""

    def __init__(self, result: IntegrationResult):
        self.result = result
        super().__init__(result.reason)
