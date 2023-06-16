from __future__ import annotations

import ast
import inspect
import os
from typing import Any, Callable


def to_object(*fn: Callable[..., Any], object_name: str):
    fn_str = "\n".join([to_str(f, indent="  ") for f in fn])
    return f"object {object_name} {{\n{fn_str}\n}}"


def to_str(fn: Callable[..., Any], indent: str = "") -> str:
    tree = ast.parse(inspect.getsource(fn))
    return translate_mod(tree, indent)


# mod
def translate_mod(node, indent: str = ""):
    return "\n".join([translate_stmt(n, indent) for n in node.body])


# stmt
def translate_stmt(node, indent: str = ""):
    if isinstance(node, ast.FunctionDef):
        args = translate_arguments(node.args)
        body = "\n".join([translate_stmt(b, indent=indent + "  ") for b in node.body])
        stmt_str = f"{indent}def {node.name}({args}) = {{\n{body}\n{indent}}}"
    elif isinstance(node, ast.Return):
        stmt_str = translate_expr(node.value, indent)
    elif isinstance(node, ast.Assign):
        value = translate_expr(node.value)
        stmt_lst = []
        for target in node.targets:
            t = translate_expr(target)
            stmt_lst.append(f"{indent}var {t} = {value}")
        stmt_str = "\n".join(stmt_lst)
        return stmt_str
    elif isinstance(node, ast.For):
        stmt_str = ""
    return stmt_str


def translate_arguments(node):
    return ",".join([translate_arg(arg) for arg in node.args])


def translate_arg(node):
    annotation = translate_annotation(node.annotation)
    return f"{node.arg}: {annotation}"


def translate_annotation(node):
    return {"int": "Integer", "float": "Double", "bool": "Boolean", "str": "String"}[node.id]


## expr ##
def translate_expr(node, indent: str = ""):
    if isinstance(node, ast.BoolOp):
        values = [translate_expr(v) for v in node.values]
        expr_str = translate_boolop(node.op, values)
    elif isinstance(node, ast.BinOp):
        left = translate_expr(node.left)
        right = translate_expr(node.right)
        expr_str = translate_operator(node.op, left, right)
    elif isinstance(node, ast.UnaryOp):
        operand = translate_expr(node.operand)
        expr_str = translate_unaryop(node.op, operand)
    elif isinstance(node, ast.Lambda):
        raise ValueError(
            "Cannot transpile lambda expression because python does not support type hinting for the arguments"
        )
    elif isinstance(node, ast.IfExp):
        test = translate_expr(node.test)
        body = translate_expr(node.body, indent=indent + "    ")
        orelse = translate_expr(node.orelse, indent=indent + "    ")
        expr_str = f"if ({test}) {{\n{body}\n  }} else {{\n{orelse}\n  }}"
    elif isinstance(node, ast.Dict):
        keys = [translate_expr(k) for k in node.keys]
        values = [translate_expr(v) for v in node.values]
        expr_str = [f"{k} -> {v}" for k, v in zip(keys, values)]
        expr_str = ", ".join(expr_str)
        expr_str = f"Map({expr_str})"
    elif isinstance(node, ast.Name):
        expr_str = node.id
    elif isinstance(node, ast.Constant):
        if node.value is True:
            expr_str = "true"
        elif node.value is False:
            expr_str = "false"
        elif isinstance(node.value, str):
            return f'"{node.value}"'
        else:
            expr_str = str(node.value)
    else:
        expr_str = ""
    return indent + expr_str


def translate_boolop(node, values):
    if isinstance(node, ast.And):
        op = " && "
    elif isinstance(node, ast.Or):
        op = " || "
    else:
        raise ValueError(f"Invalid node {node} for boolop")
    return f"({op.join(values)})"


def translate_operator(node, left, right):
    if isinstance(node, ast.Add):
        op_str = f"{left} + {right}"
    elif isinstance(node, ast.Sub):
        op_str = f"{left} - {right}"
    elif isinstance(node, ast.Mult):
        op_str = f"{left} * {right}"
    elif isinstance(node, ast.Div):
        op_str = f"{left} / {right}"
    elif isinstance(node, ast.Mod):
        op_str = f"{left} % {right}"
    elif isinstance(node, ast.Pow):
        op_str = f"scala.math.pow({left}.toDouble, {right}.toDouble)"
    elif isinstance(node, ast.LShift):
        op_str = f"{left} << {right}"
    elif isinstance(node, ast.RShift):
        op_str = f"{left} >> {right}"
    elif isinstance(node, ast.BitOr):
        op_str = f"{left} | {right}"
    elif isinstance(node, ast.BitXor):
        op_str = f"{left} ^ {right}"
    elif isinstance(node, ast.BitAnd):
        op_str = f"{left} & {right}"
    elif isinstance(node, ast.FloorDiv):
        op_str = f"scala.math.floorDiv({left}.toLong, {right}.toLong)"
    return f"({op_str})"


def translate_unaryop(node, operand):
    if isinstance(node, ast.Invert):
        return f"!({operand})"
    elif isinstance(node, ast.Not):
        return f"!({operand})"
    elif isinstance(node, ast.UAdd):
        return f"+({operand})"
    elif isinstance(node, ast.USub):
        return f"-({operand})"


__all__ = ["to_object", "to_str"]
