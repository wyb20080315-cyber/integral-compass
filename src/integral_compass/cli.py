"""Command-line interface."""

import argparse
import json

from .api import analyze
from .parser import ExpressionError


def main(argv=None):
    parser = argparse.ArgumentParser(description="Explain and verify elementary integration")
    parser.add_argument("expression", help="Quoted expression, e.g. 'x**2 * exp(x)'")
    parser.add_argument("--variable", default="x")
    parser.add_argument("--depth", type=int, default=None,
                        help="Maximum level, counting the original integral as 1")
    parser.add_argument("--classic", action="store_true", help="Use the 0.1 Risch-based API")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        if args.classic:
            if args.depth is not None:
                parser.error("--classic cannot be combined with --depth")
            from .classic import analyze as classic_analyze
            result = classic_analyze(args.expression, args.variable, timeout=args.timeout)
        else:
            result = analyze(args.expression, args.depth, variable=args.variable, timeout=args.timeout)
    except (ExpressionError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
          if args.as_json else result.explain())
    return 3 if result.status == "unknown" else 0
