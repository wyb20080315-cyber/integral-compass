"""A deliberately small expression language; never eval user expressions."""

import ast
import re

import sympy as sp


class ExpressionError(ValueError):
    """The input is outside the supported one-variable expression language."""


FUNCTIONS = {
    name: getattr(sp, name)
    for name in ("sin", "cos", "tan", "cot", "sec", "csc", "asin", "acos", "atan",
                 "exp", "log", "sqrt", "Abs")
}
CONSTANTS = {"pi": sp.pi, "E": sp.E, "I": sp.I}


def make_symbol(variable: str | sp.Symbol) -> sp.Symbol:
    if isinstance(variable, sp.Symbol):
        symbol = variable
    elif isinstance(variable, str):
        symbol = sp.Symbol(variable, real=True)
    else:
        raise ExpressionError("variable must be a name or a SymPy Symbol")
    if (not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,31}", symbol.name)
            or symbol.name in FUNCTIONS or symbol.name in CONSTANTS):
        raise ExpressionError("Use a simple variable name such as x or t")
    return symbol


def parse_expression(value: str | sp.Expr, symbol: sp.Symbol) -> sp.Expr:
    if isinstance(value, sp.Expr):
        # Reject unknown functions, derivatives and foreign symbols before serialization.
        if value.free_symbols - {symbol}:
            raise ExpressionError("Only the integration variable is supported; no parameters")
        value = str(value)
    if not isinstance(value, str) or not value.strip() or len(value) > 2000:
        raise ExpressionError("Provide a nonempty expression of at most 2000 characters")
    try:
        tree = ast.parse(value, mode="eval")
    except (SyntaxError, RecursionError) as exc:
        raise ExpressionError("Invalid expression; use ** for powers and * for products") from exc
    if sum(1 for _ in ast.walk(tree)) > 200:
        raise ExpressionError("Expression is too large (maximum 200 syntax nodes)")

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            literal = ast.get_source_segment(value, node)
            number = sp.Rational(literal)
            if max(abs(number.p).bit_length(), number.q.bit_length()) > 128:
                raise ExpressionError("Numeric literal is too large")
            return number
        if isinstance(node, ast.Name):
            if node.id == symbol.name:
                return symbol
            if node.id in CONSTANTS:
                return CONSTANTS[node.id]
            raise ExpressionError(f"Unknown name: {node.id}")
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            child = visit(node.operand)
            return -child if isinstance(node.op, ast.USub) else child
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                result = left + right
            elif isinstance(node.op, ast.Sub):
                result = left - right
            elif isinstance(node.op, ast.Mult):
                result = left * right
            elif isinstance(node.op, ast.Div):
                if right == 0:
                    raise ExpressionError("Division by zero")
                result = left / right
            elif isinstance(node.op, ast.Pow):
                if right.is_number and (right.is_real is not True or abs(right) > 100):
                    raise ExpressionError("Numeric exponents must be real and between -100 and 100")
                result = left**right
            else:
                raise ExpressionError("Only +, -, *, /, and ** operators are supported")
            if isinstance(result, sp.Rational) and max(
                    abs(result.p).bit_length(), result.q.bit_length()) > 4096:
                raise ExpressionError("Computed number is too large")
            return result
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in FUNCTIONS and len(node.args) == 1 and not node.keywords):
            return FUNCTIONS[node.func.id](visit(node.args[0]))
        raise ExpressionError("Unsupported syntax; attributes, indexing and code are not allowed")

    try:
        expression = visit(tree.body)
    except ExpressionError:
        raise
    except (ValueError, TypeError, OverflowError, ZeroDivisionError, RecursionError) as exc:
        raise ExpressionError("Invalid mathematical expression") from exc
    if expression.has(sp.oo, -sp.oo, sp.zoo, sp.nan):
        raise ExpressionError("The expression must be finite as a symbolic expression")
    return expression
