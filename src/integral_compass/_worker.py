"""Private worker. JSON input and output; no executable expression deserialization."""

import json
import sys

import sympy as sp

from .engine import analyze_core
from .models import IntegrationResult
from .parser import parse_expression
from .search import search_core


def main():
    data = json.load(sys.stdin)
    x = sp.Symbol(data["variable"], **data["assumptions"])
    f = parse_expression(data["expression"], x)
    try:
        result = (analyze_core(f, x) if data.get("mode") == "classic"
                  else search_core(f, x, data.get("depth")))
    except Exception:  # noqa: BLE001 -- worker boundary converts backend faults to unknown
        result = IntegrationResult("unknown", f, x, method="backend_error", reason=
                                   "The symbolic backend could not process this expression.")
    print(json.dumps(result.to_dict()))


if __name__ == "__main__":
    main()
