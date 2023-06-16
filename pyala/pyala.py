from __future__ import annotations

import ast
import inspect
import os
from typing import Any, Callable


def to_object(*fn: Callable[..., Any], object_name: str):
    fn_str = "\n".join([Transpiler(f).to_str("  ") for f in fn])
    return f"object {object_name} {{\n{fn_str}\n}}"


def to_str(fn: Callable[..., Any], indent: str = "") -> str:
    return Transpiler(fn).to_str(indent)


class Transpiler:
    def __init__(self, fn: Callable[..., Any]):
        self.fn = fn

    def to_str(self, indent="") -> str:
        self._names: dict[str, Any] = {}
        tree = ast.parse(inspect.getsource(self.fn))
        return self.translate_mod(tree, indent)

    # mod
    def translate_mod(self, node, indent: str = ""):
        return "\n".join([self.translate_stmt(n, indent) for n in node.body])

    def translate_stmt(self, node, indent: str = ""):
        if isinstance(node, ast.FunctionDef):
            args = self.translate_arguments(node.args)
            body = "\n".join([self.translate_stmt(b, indent=indent + "  ") for b in node.body])
            stmt_str = f"{indent}def {node.name}({args}) = {{\n{body}\n{indent}}}"
        elif isinstance(node, ast.Return):
            stmt_str = self.translate_expr(node.value, indent)
        elif isinstance(node, ast.Assign):
            value = self.translate_expr(node.value)
            stmt_lst = []
            for target in node.targets:
                t = self.translate_expr(target)
                var = "var " if self._names[t] == 1 else ""
                stmt_lst.append(f"{indent}{var}{t} = {value}")
            stmt_str = "\n".join(stmt_lst)
            return stmt_str
        elif isinstance(node, ast.For):
            stmt_str = ""
        return stmt_str

    def translate_arguments(self, node):
        return ",".join([self.translate_arg(arg) for arg in node.args])

    def translate_arg(self, node):
        annotation = self.translate_annotation(node.annotation)
        return f"{node.arg}: {annotation}"

    def translate_annotation(self, node):
        return {"int": "Integer", "float": "Double", "bool": "Boolean", "str": "String"}[node.id]

    ## expr ##
    def translate_expr(self, node, indent: str = ""):
        if isinstance(node, ast.BoolOp):
            values = [self.translate_expr(v) for v in node.values]
            expr_str = self.translate_boolop(node.op, values)
        elif isinstance(node, ast.BinOp):
            left = self.translate_expr(node.left)
            right = self.translate_expr(node.right)
            expr_str = self.translate_operator(node.op, left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self.translate_expr(node.operand)
            expr_str = self.translate_unaryop(node.op, operand)
        elif isinstance(node, ast.Lambda):
            raise ValueError(
                "Cannot transpile lambda expression because python does not support type hinting for the arguments"
            )
        elif isinstance(node, ast.IfExp):
            test = self.translate_expr(node.test)
            body = self.translate_expr(node.body, indent=indent + "    ")
            orelse = self.translate_expr(node.orelse, indent=indent + "    ")
            expr_str = f"if ({test}) {{\n{body}\n  }} else {{\n{orelse}\n  }}"
        elif isinstance(node, ast.Dict):
            keys = [self.translate_expr(k) for k in node.keys]
            values = [self.translate_expr(v) for v in node.values]
            expr_str = [f"{k} -> {v}" for k, v in zip(keys, values)]
            expr_str = ", ".join(expr_str)
            expr_str = f"Map({expr_str})"
        elif isinstance(node, ast.Name):
            self._names[node.id] = self._names.get(node.id, 0) + 1
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

    def translate_boolop(self, node, values):
        if isinstance(node, ast.And):
            op = " && "
        elif isinstance(node, ast.Or):
            op = " || "
        else:
            raise ValueError(f"Invalid node {node} for boolop")
        return f"({op.join(values)})"

    def translate_operator(self, node, left, right):
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

    def translate_unaryop(self, node, operand):
        if isinstance(node, ast.Invert):
            return f"!({operand})"
        elif isinstance(node, ast.Not):
            return f"!({operand})"
        elif isinstance(node, ast.UAdd):
            return f"+({operand})"
        elif isinstance(node, ast.USub):
            return f"-({operand})"


__all__ = ["to_object", "to_str"]
