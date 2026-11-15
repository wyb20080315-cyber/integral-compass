"""Private worker. JSON input and output; no executable expression deserialization."""

import json
import sys

import sympy as sp

from .engine import analyze_core
from .models import IntegrationResult
from .parser import parse_expression
from .risch_backend import risch_decision
from .search import search_core


def main():
    data = json.load(sys.stdin)
    x = sp.Symbol(data["variable"], **data["assumptions"])
    f = parse_expression(data["expression"], x)
    try:
        if data.get("mode") == "classic":
            result = analyze_core(f, x)
        elif data.get("mode") == "risch":
            result = risch_decision(f, x)
        else:
            result = search_core(f, x, data.get("depth"))
    except Exception:  # noqa: BLE001 -- worker boundary converts backend faults to unknown
        result = IntegrationResult("unknown", f, x, method="backend_error", reason=
                                   "The symbolic backend could not process this expression.",
                                   reason_code="backend_error")
    print(json.dumps(result.to_dict()))


if __name__ == "__main__":
    main()
