"""Command-line interface."""

import argparse
import json

from .api import analyze
from .parser import ExpressionError


def main(argv=None):
    parser = argparse.ArgumentParser(description="Explain and verify elementary integration")
    parser.add_argument("expression", help="Quoted expression, e.g. 'x**2 * exp(x)'")
    parser.add_argument("--variable", default="x")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        result = analyze(args.expression, args.variable, timeout=args.timeout)
    except (ExpressionError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
          if args.as_json else result.explain())
    return 3 if result.status == "unknown" else 0
