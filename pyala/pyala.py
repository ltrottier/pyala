from __future__ import annotations

import ast
import inspect
import os
from typing import Any, Callable

from parse import parse


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
        if isinstance(node, ast.Module):
            mod_str = "\n".join([self.translate_stmt(n, indent) for n in node.body])
        elif isinstance(node, ast.Interactive):
            raise NotImplementedError
        elif isinstance(node, ast.Expression):
            mod_str = self.translate_expr(node, indent)
        elif isinstance(node, ast.FunctionType):
            raise NotImplementedError
        else:
            raise ValueError(f"Invalid node {node} for mod")
        return mod_str

    def translate_stmt(self, node, indent: str = ""):
        if isinstance(node, ast.FunctionDef):
            args = self.translate_arguments(node.args)
            body = "\n".join([self.translate_stmt(b, indent=indent + "  ") for b in node.body])
            stmt_str = f"{indent}def {node.name}({args}) = {{\n{body}\n{indent}}}"
        elif isinstance(node, ast.AsyncFunctionDef):
            raise NotImplementedError
        elif isinstance(node, ast.ClassDef):
            raise NotImplementedError
        elif isinstance(node, ast.Return):
            stmt_str = f"{indent}" + self.translate_expr(node.value, indent)
        elif isinstance(node, ast.Delete):
            raise NotImplementedError
        elif isinstance(node, ast.Assign):
            value = self.translate_expr(node.value, indent)
            stmt_lst = []
            for target in node.targets:
                t = self.translate_expr(target)
                if t.startswith("Range("):  # target is an ast.Slice
                    r, v = parse("{}.map({}(_))", t)
                    stmt_lst.append(
                        f"{indent}{r}.zip({value}).foreach {{(i, v) => {v}.insert(i, v) }}"
                    )
                else:
                    var = "var " if self._names[t] == 1 else ""
                    stmt_lst.append(f"{indent}{var}{t} = {value}")
            stmt_str = "\n".join(stmt_lst)
            return stmt_str
        elif isinstance(node, ast.AugAssign):
            raise NotImplementedError
        elif isinstance(node, ast.AnnAssign):
            raise NotImplementedError
        elif isinstance(node, ast.For):
            raise NotImplementedError
        elif isinstance(node, ast.AsyncFor):
            raise NotImplementedError
        elif isinstance(node, ast.While):
            raise NotImplementedError
        elif isinstance(node, ast.If):
            raise NotImplementedError
        elif isinstance(node, ast.With):
            raise NotImplementedError
        elif isinstance(node, ast.AsyncWith):
            raise NotImplementedError
        elif isinstance(node, ast.Match):
            raise NotImplementedError
        elif isinstance(node, ast.Raise):
            raise NotImplementedError
        elif isinstance(node, ast.Try):
            raise NotImplementedError
        elif isinstance(node, ast.Assert):
            raise NotImplementedError
        elif isinstance(node, ast.Import):
            raise NotImplementedError
        elif isinstance(node, ast.ImportFrom):
            raise NotImplementedError
        elif isinstance(node, ast.Global):
            raise NotImplementedError
        elif isinstance(node, ast.Nonlocal):
            raise NotImplementedError
        elif isinstance(node, ast.Expr):
            stmt_str = self.translate_expr(node, indent)
        elif isinstance(node, ast.Pass):
            raise NotImplementedError
        elif isinstance(node, ast.Break):
            raise NotImplementedError
        elif isinstance(node, ast.Continue):
            raise NotImplementedError
        else:
            raise ValueError(f"Invalid node {node} for stmt")
        return stmt_str

    ## expr ##
    def translate_expr(self, node, indent: str = ""):
        if isinstance(node, ast.BoolOp):
            values = [self.translate_expr(v) for v in node.values]
            expr_str = self.translate_boolop(node.op, values)
        elif isinstance(node, ast.NamedExpr):
            raise NotImplementedError
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
        elif isinstance(node, ast.Set):
            raise NotImplementedError
        elif isinstance(node, ast.ListComp):
            elt = self.translate_expr(node.elt)
            gen = [self.translate_comprehension(g, indent + "  ") for g in node.generators]
            gen_str = "\n".join(gen)
            expr_str = f"for {{\n{gen_str}\n{indent}}} yield {elt}"
        elif isinstance(node, ast.SetComp):
            raise NotImplementedError
        elif isinstance(node, ast.DictComp):
            raise NotImplementedError
        elif isinstance(node, ast.GeneratorExp):
            raise NotImplementedError
        # the grammar constrains where yield expressions can occur
        elif isinstance(node, ast.Await):
            raise NotImplementedError
        elif isinstance(node, ast.Yield):
            raise NotImplementedError
        elif isinstance(node, ast.YieldFrom):
            raise NotImplementedError
        # need sequences for compare to distinguish between
        elif isinstance(node, ast.Compare):
            left = self.translate_expr(node.left)
            ops = [self.translate_cmpop(o) for o in node.ops]
            comparators = [self.translate_expr(c) for c in node.comparators]
            expr_list: list[str] = []
            for op, right in zip(ops, comparators):
                if len(expr_list) != 0:
                    expr_list.append("&&")
                expr_list.append(f"({left} {op} {right})")
                left = right
            expr_str = " ".join(expr_list)
        elif isinstance(node, ast.Call):
            raise NotImplementedError
        elif isinstance(node, ast.FormattedValue):
            raise NotImplementedError
        elif isinstance(node, ast.JoinedStr):
            raise NotImplementedError
        elif isinstance(node, ast.Constant):
            if node.value is True:
                expr_str = "true"
            elif node.value is False:
                expr_str = "false"
            elif isinstance(node.value, str):
                return f'"{node.value}"'
            else:
                expr_str = str(node.value)
        # the following expression can appear in assignment context
        elif isinstance(node, ast.Attribute):
            raise NotImplementedError
        elif isinstance(node, ast.Subscript):
            val = self.translate_expr(node.value, indent)
            slce = self.translate_expr(node.slice, indent)
            expr_str = f"{slce}.map({val}(_))"
        elif isinstance(node, ast.Starred):
            raise NotImplementedError
        elif isinstance(node, ast.Name):
            self._names[node.id] = self._names.get(node.id, 0) + 1
            expr_str = node.id
        elif isinstance(node, ast.List):
            expr_str = ", ".join([self.translate_expr(e) for e in node.elts])
            expr_str = f"scala.collection.mutable.Buffer({expr_str})"
        elif isinstance(node, ast.Tuple):
            expr_str = ", ".join([self.translate_expr(e) for e in node.elts])
            expr_str = f"({expr_str})"
        # can appear only in Subscript
        elif isinstance(node, ast.Slice):
            lower = self.translate_expr(node.lower) if node.lower is not None else "0"
            upper = self.translate_expr(node.upper) if node.upper is not None else "Int.MaxValue"
            step = self.translate_expr(node.step) if node.step is not None else "1"
            expr_str = f"Range({lower}, {upper}, {step})"
        else:
            raise ValueError(f"Invalid node {node} for expr")
        return expr_str

    def translate_expr_context(self, node):
        expr_str = ""
        if isinstance(node, ast.Load):
            raise NotImplementedError
        elif isinstance(node, ast.Store):
            raise NotImplementedError
        elif isinstance(node, ast.Del):
            raise NotImplementedError
        else:
            raise ValueError(f"Invalid node {node} for expr_context")
        return expr_str

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
        elif isinstance(node, ast.MatMult):
            raise NotImplementedError
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
        else:
            raise ValueError(f"Invalid node {node} for operator")

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
        else:
            raise ValueError(f"Invalid node {node} for unaryop")

    def translate_cmpop(self, node):
        cmpop_str = ""
        if isinstance(node, ast.Eq):
            cmpop_str = " == "
        elif isinstance(node, ast.NotEq):
            cmpop_str = " != "
        elif isinstance(node, ast.Lt):
            cmpop_str = " < "
        elif isinstance(node, ast.LtE):
            cmpop_str = " <= "
        elif isinstance(node, ast.Gt):
            cmpop_str = " > "
        elif isinstance(node, ast.GtE):
            cmpop_str = " >= "
        elif isinstance(node, ast.Is):
            cmpop_str = " eq "
        elif isinstance(node, ast.IsNot):
            cmpop_str = " ne "
        elif isinstance(node, ast.NotIn):
            raise NotImplementedError
        else:
            raise ValueError(f"Invalid node {node} for cmpop")
        return cmpop_str

    def translate_comprehension(self, node, indent=""):
        target = self.translate_expr(node.target)
        iterr = self.translate_expr(node.iter)
        ifs = [self.translate_expr(i) for i in node.ifs]
        ifs = " && ".join(ifs)
        c_str = f"{indent}{target} <- {iterr} if ({ifs})"
        return c_str

    def translate_excepthandler(self, node):
        raise NotImplementedError

    def translate_arguments(self, node):
        return ",".join([self.translate_arg(arg) for arg in node.args])

    def translate_arg(self, node):
        annotation = self.translate_annotation(node.annotation)
        return f"{node.arg}: {annotation}"

    def translate_keyword(self, node):
        raise NotImplementedError

    def translate_alias(self, node):
        raise NotImplementedError

    def translate_match_case(self, node):
        raise NotImplementedError

    def translate_pattern(self, node):
        if isinstance(node, ast.MatchValue):
            raise NotImplementedError
        elif isinstance(node, ast.MatchSingleton):
            raise NotImplementedError
        elif isinstance(node, ast.MatchSequence):
            raise NotImplementedError
        elif isinstance(node, ast.MatchMapping):
            raise NotImplementedError
        elif isinstance(node, ast.MatchClass):
            raise NotImplementedError
        elif isinstance(node, ast.MatchStar):
            raise NotImplementedError
        elif isinstance(node, ast.MatchAs):
            raise NotImplementedError
        elif isinstance(node, ast.MatchOr):
            raise NotImplementedError
        else:
            raise ValueError(f"Invalid node {node} for pattern")

    def translate_type_ignore(self, node):
        raise NotImplementedError

    def translate_annotation(self, node):
        return {"int": "Integer", "float": "Double", "bool": "Boolean", "str": "String"}[node.id]


__all__ = ["to_object", "to_str"]
