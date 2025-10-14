"""Computation tools for mathematical and code execution."""

from __future__ import annotations

import ast
import math
import operator
from typing import Any


# Safe operators for evaluation
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Safe functions
SAFE_FUNCTIONS = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "len": len,
    # Math functions
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "floor": math.floor,
    "ceil": math.ceil,
    "pi": math.pi,
    "e": math.e,
}


def safe_eval(expression: str) -> float | int:
    """Safely evaluate a mathematical expression.

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        Result of the evaluation

    Raises:
        ValueError: If expression contains unsafe operations
    """

    def _eval_node(node: ast.expr) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            op = SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {node.op.__class__.__name__}")
            return op(left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = _eval_node(node.operand)
            op = SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {node.op.__class__.__name__}")
            return op(operand)
        elif isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else None
            if func_name not in SAFE_FUNCTIONS:
                raise ValueError(f"Unsupported function: {func_name}")
            func = SAFE_FUNCTIONS[func_name]
            args = [_eval_node(arg) for arg in node.args]
            return func(*args)
        elif isinstance(node, ast.Name):
            # Allow math constants
            if node.id in SAFE_FUNCTIONS:
                return SAFE_FUNCTIONS[node.id]
            raise ValueError(f"Unknown variable: {node.id}")
        else:
            raise ValueError(f"Unsupported expression type: {node.__class__.__name__}")

    try:
        tree = ast.parse(expression, mode="eval")
        return _eval_node(tree.body)
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {str(e)}")


def calculate(expression: str) -> str:
    """Calculate a mathematical expression safely.

    Args:
        expression: Mathematical expression (e.g., "2 + 2", "sqrt(16)")

    Returns:
        Calculation result as string
    """
    try:
        result = safe_eval(expression)
        return f"{expression} = {result}"
    except ValueError as e:
        return f"Calculation error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def python_eval(code: str) -> str:
    """Evaluate simple Python expressions (very restricted).

    WARNING: This is highly restricted for security. Only allows:
    - Mathematical expressions
    - List/dict comprehensions with safe operations
    - Basic data structures (list, dict, tuple, set)

    Args:
        code: Python expression to evaluate

    Returns:
        Evaluation result as string
    """
    try:
        # Parse and validate AST
        tree = ast.parse(code, mode="eval")

        # Check for unsafe operations
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef)):
                return "Error: Imports and definitions not allowed"
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id not in SAFE_FUNCTIONS and node.func.id not in (
                        "list",
                        "dict",
                        "tuple",
                        "set",
                        "str",
                        "int",
                        "float",
                    ):
                        return f"Error: Function '{node.func.id}' not allowed"

        # Evaluate with restricted builtins
        result = eval(
            compile(tree, "<string>", "eval"),
            {"__builtins__": {}},
            SAFE_FUNCTIONS,
        )

        return str(result)

    except SyntaxError as e:
        return f"Syntax error: {str(e)}"
    except Exception as e:
        return f"Evaluation error: {str(e)}"


def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between common units.

    Supported conversions:
    - Length: m, km, mi, ft, in
    - Weight: kg, g, lb, oz
    - Temperature: c, f, k

    Args:
        value: Value to convert
        from_unit: Source unit
        to_unit: Target unit

    Returns:
        Conversion result as string
    """
    # Length conversions (to meters)
    length_to_m = {
        "m": 1.0,
        "km": 1000.0,
        "mi": 1609.34,
        "ft": 0.3048,
        "in": 0.0254,
    }

    # Weight conversions (to kg)
    weight_to_kg = {
        "kg": 1.0,
        "g": 0.001,
        "lb": 0.453592,
        "oz": 0.0283495,
    }

    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    # Temperature conversions (special case)
    if from_unit in ("c", "f", "k") and to_unit in ("c", "f", "k"):
        # Convert to Celsius first
        if from_unit == "f":
            celsius = (value - 32) * 5 / 9
        elif from_unit == "k":
            celsius = value - 273.15
        else:
            celsius = value

        # Convert from Celsius to target
        if to_unit == "f":
            result = celsius * 9 / 5 + 32
        elif to_unit == "k":
            result = celsius + 273.15
        else:
            result = celsius

        return f"{value} {from_unit.upper()} = {result:.2f} {to_unit.upper()}"

    # Length conversion
    if from_unit in length_to_m and to_unit in length_to_m:
        meters = value * length_to_m[from_unit]
        result = meters / length_to_m[to_unit]
        return f"{value} {from_unit} = {result:.4f} {to_unit}"

    # Weight conversion
    if from_unit in weight_to_kg and to_unit in weight_to_kg:
        kg = value * weight_to_kg[from_unit]
        result = kg / weight_to_kg[to_unit]
        return f"{value} {from_unit} = {result:.4f} {to_unit}"

    return f"Error: Unsupported conversion from {from_unit} to {to_unit}"


class ComputationTool:
    """Collection of computation tools for agents."""

    @staticmethod
    def calculate(expression: str) -> str:
        """Perform mathematical calculation.

        Args:
            expression: Math expression

        Returns:
            Calculation result
        """
        return calculate(expression)

    @staticmethod
    def eval(code: str) -> str:
        """Evaluate Python expression (restricted).

        Args:
            code: Python expression

        Returns:
            Evaluation result
        """
        return python_eval(code)

    @staticmethod
    def convert(value: float, from_unit: str, to_unit: str) -> str:
        """Convert between units.

        Args:
            value: Value to convert
            from_unit: Source unit
            to_unit: Target unit

        Returns:
            Conversion result
        """
        return convert_units(value, from_unit, to_unit)
