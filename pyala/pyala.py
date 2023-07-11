from __future__ import annotations

import ast
import inspect
import os
from typing import Any

from parse import parse

GLOBAL_IMPORTS = """import scala.util.control.Breaks._
import scala.math

"""


def to_file(*fn: Any, filepath: str) -> str:
    object_name = os.path.splitext(filepath.split(os.sep)[-1])[0]
    bin_op_str = to_object(*fn, object_name=object_name)
    with open(filepath, "w") as fid:
        fid.write("// This file was auto-generated\n")
        fid.write(bin_op_str)
        fid.write("\n")
    return bin_op_str


def to_object(*fn: Any, object_name: str, with_global_imports: bool = True) -> str:
    fn_str = "\n".join([Transpiler(f).to_str("  ", False) for f in fn])
    return f"{GLOBAL_IMPORTS}object {object_name} {{\n{fn_str}\n}}"


def to_str(fn: Any, indent: str = "") -> str:
    return Transpiler(fn).to_str(indent)


class Transpiler:
    def __init__(self, fn: Any):
        self.fn = fn

    def to_str(self, indent="", with_global_imports: bool = True) -> str:
        self._names: dict[str, Any] = {}
        tree = ast.parse(inspect.getsource(self.fn))
        tree_str = self.translate_mod(tree, indent)
        if with_global_imports:
            return f"{GLOBAL_IMPORTS}{tree_str}"
        else:
            return tree_str

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
            target = self.translate_expr(node.target)
            value = self.translate_expr(node.value)
            op = self.translate_operator(node.op, target, value)
            stmt_str = f"{indent}{target} = {op}"
        elif isinstance(node, ast.AnnAssign):
            target = self.translate_expr(node.target)
            annotation = self.translate_annotation(node.annotation)
            value = " = " + self.translate_expr(node.value) if node.value is not None else ""
            stmt_str = f"{indent}var {target}: {annotation}{value}"
        elif isinstance(node, ast.For):
            target = self.translate_expr(node.target)
            itr = self.translate_expr(node.iter)
            body_lst = [self.translate_stmt(b, indent=indent + "  ") for b in node.body]
            body = "\n".join(body_lst)
            orelse_lst = [self.translate_stmt(b, indent=indent + "  ") for b in node.orelse]
            if len(orelse_lst) != 0:
                raise NotImplementedError(
                    f"for/else are not supported:\n{ast.dump(node, indent=2)}"
                )
            stmt_str = f"{indent}breakable{{for ({target} <- {itr}) {{\n{body}\n{indent}}}}}"
        elif isinstance(node, ast.AsyncFor):
            raise NotImplementedError(f"async for is not supported:\n{ast.dump(node, indent=2)}")
        elif isinstance(node, ast.While):
            test = self.translate_expr(node.test, indent)
            body_lst = [self.translate_stmt(b, indent=indent + "  ") for b in node.body]
            body = "\n".join(body_lst)
            orelse_lst = [self.translate_stmt(b, indent=indent + "  ") for b in node.orelse]
            if len(orelse_lst) != 0:
                raise NotImplementedError(
                    f"while/else are not supported:\n{ast.dump(node, indent=2)}"
                )
            stmt_str = f"{indent}breakable{{while ({test}) {{\n{body}\n{indent}}}}}"
        elif isinstance(node, ast.If):
            test = self.translate_expr(node.test, indent)
            body_lst = [self.translate_stmt(b, indent=indent + "  ") for b in node.body]
            body = "\n".join(body_lst)
            orelse_lst = [self.translate_stmt(b, indent=indent + "  ") for b in node.orelse]
            orelse = "\n".join(orelse_lst)
            stmt_str = f"{indent}if {test} {{\n{body}\n{indent}}} else {{\n{orelse}\n{indent}}}"
        elif isinstance(node, ast.With):
            raise NotImplementedError(
                f"Context managers (with) are not supported:\n{ast.dump(node, indent=2)}"
            )
        elif isinstance(node, ast.AsyncWith):
            raise NotImplementedError(
                f"Async context managers are not supported:\n{ast.dump(node, indent=2)}"
            )
        elif isinstance(node, ast.Raise):
            exc = "Exception()" if node.exc is None else self.translate_expr(node.exc)
            stmt_str = f"{indent}throw new {exc}"
        elif isinstance(node, ast.Try):
            raise NotImplementedError
        elif isinstance(node, ast.Assert):
            test = self.translate_expr(node.test)
            msg = "" if node.msg is None else self.translate_expr(node.msg)
            stmt_str = f"{indent}assert({test}, {msg})"
        elif isinstance(node, ast.Import):
            raise NotImplementedError("import is not supported")
            # aliases_lst = [f"{indent}import " + self.translate_alias(name) for name in node.names]
            # stmt_str = "\n".join(aliases_lst)
        elif isinstance(node, ast.ImportFrom):
            raise NotImplementedError("import is not supported")
            # module = node.module
            # if module == "math":
            #     module = "scala.math"
            # aliases_lst = [
            #     f"{indent}import {module}." + self.translate_alias(name) for name in node.names
            # ]
            # level = node.level
            # stmt_str = "\n".join(aliases_lst)
        elif isinstance(node, ast.Global):
            raise NotImplementedError
        elif isinstance(node, ast.Nonlocal):
            raise NotImplementedError
        elif isinstance(node, ast.Expr):
            stmt_str = self.translate_expr(node, indent)
        elif isinstance(node, ast.Pass):
            stmt_str = f"{indent}()"
        elif isinstance(node, ast.Break):
            stmt_str = f"{indent}break"
        elif isinstance(node, ast.Continue):
            raise NotImplementedError(
                f"For loops with continue are not supported:\n{ast.dump(node, indent=2)}"
            )
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
            raise ValueError(f"lambda expressions are not supported:\n{ast.dump(node, indent=2)}")
        elif isinstance(node, ast.IfExp):
            test = self.translate_expr(node.test)
            body = self.translate_expr(node.body, indent=indent + "    ")
            orelse = self.translate_expr(node.orelse, indent=indent + "    ")
            expr_str = f"if ({test}) {{\n{body}\n  }} else {{\n{orelse}\n  }}"
        elif isinstance(node, ast.Dict):
            keys = [self.translate_expr(k) for k in node.keys]
            values = [self.translate_expr(v) for v in node.values]
            expr_lst = [f"{k} -> {v}" for k, v in zip(keys, values)]
            expr_str = ", ".join(expr_lst)
            expr_str = f"scala.collection.mutable.Map({expr_str})"
        elif isinstance(node, ast.Set):
            elts = [self.translate_expr(e) for e in node.elts]
            expr_str = ", ".join(elts)
            expr_str = f"scala.collection.mutable.Set({expr_str})"
        elif isinstance(node, ast.ListComp):
            elt = self.translate_expr(node.elt)
            gen = [self.translate_comprehension(g, indent + "  ") for g in node.generators]
            gen_str = "\n".join(gen)
            expr_str = f"for {{\n{gen_str}\n{indent}}} yield {elt}"
        elif isinstance(node, ast.SetComp):
            elt = self.translate_expr(node.elt)
            gen = [self.translate_comprehension(g, indent + "  ") for g in node.generators]
            gen_str = "\n".join(gen)
            expr_str = f"for {{\n{gen_str}\n{indent}}} yield {elt}"
            expr_str = f"scala.collection.mutable.Set(({expr_str}).toSeq: _*)"
        elif isinstance(node, ast.DictComp):
            key = self.translate_expr(node.key)
            value = self.translate_expr(node.value)
            gen = [self.translate_comprehension(g, indent + "  ") for g in node.generators]
            gen_str = "\n".join(gen)
            expr_str = f"for {{\n{gen_str}\n{indent}}} yield {key} -> {value}"
            expr_str = f"scala.collection.mutable.Map(({expr_str}).toSeq: _*)"
        elif isinstance(node, ast.GeneratorExp):
            raise ValueError(
                f"generator expressions are not supported:\n{ast.dump(node, indent=2)}"
            )
        # the grammar constrains where yield expressions can occur
        elif isinstance(node, ast.Await):
            raise ValueError(f"async and await are not supported:\n{ast.dump(node, indent=2)}")
        elif isinstance(node, ast.Yield):
            raise ValueError(
                f"generator expressions are not supported:\n{ast.dump(node, indent=2)}"
            )
        elif isinstance(node, ast.YieldFrom):
            raise ValueError(
                f"generator expressions are not supported:\n{ast.dump(node, indent=2)}"
            )
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
            args_list = [self.translate_expr(args, indent=indent + "  ") for args in node.args]
            keywords_list = [
                self.translate_keyword(keywords, indent=indent + "  ") for keywords in node.keywords
            ]
            args_lst = args_list + keywords_list
            expr_str = self.translate_func(node.func, args_lst)
        elif isinstance(node, ast.FormattedValue):
            value = self.translate_expr(node.value)
            format_spec = "" if node.format_spec is None else self.translate_expr(node.format_spec)
            format_spec = format_spec.replace('"', "").lstrip("0")
            expr_str = f'f"${value}%{format_spec}"'
        elif isinstance(node, ast.JoinedStr):
            values_lst = [self.translate_expr(value) for value in node.values]
            expr_str = " + ".join(values_lst)
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
            value = self.translate_expr(node.value)
            attr = node.attr
            expr_str = f"{value}.{attr}"
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

    def translate_func(self, node, args_lst: list[str]):
        """Translations for callables.
        We consider:
         1. builtins: https://docs.python.org/3/library/functions.html
         2. math functions: https://docs.python.org/3/library/math.html

        """
        func = self.translate_expr(node)
        args = ", ".join(args_lst)
        if func.endswith("Error"):
            return f"Exception({args})"
        # built-in functions: https://docs.python.org/3/library/functions.html
        elif func == "abs":
            return f"math.abs({args})"
        elif func == "aiter":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "all":
            return f"{args}.forall(x => x)"
        elif func == "any":
            return f"{args}.exists(x => x)"
        elif func == "anext":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "ascii":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "bin":
            return f'"0b" + {args}.toBinaryString'
        elif func == "bool":
            return f"{args}.toBoolean"
        elif func == "breakpoint":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "bytearray":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "bytes":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "callable":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "chr":
            return f"{args}.toChar.toString"
        elif func == "classmethod":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "compile":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "complex":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "delattr":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "dict":
            return f"scala.collection.mutable.Map({args.replace('=', '<-')})"
        elif func == "dir":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "divmod":
            dividend = args_lst[0]
            divisor = args_lst[1]
            return f"({dividend} / {divisor}, {dividend} % {divisor})"
        elif func == "enumerate":
            return f"{args}.zipWithIndex.map((elem, idx) => (idx, elem))"
        elif func == "eval":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "exec":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "filter":
            cond, iterable = args_lst
            return f"{iterable}.filter({cond})"
        elif func == "float":
            return f"{args}.toDouble"
        elif func == "format":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "frozenset":
            return f"{args}.toSet"
        elif func == "getattr":
            if len(args_lst) == 2:
                raise NotImplementedError("getattr with a default value is not supported.")
            obj = args_lst[0]
            name = args_lst[1]
            return f"{obj}.{name}"
        elif func == "globals":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "hasattr":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "hash":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "help":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "hex":
            return f'"0x" + {args}.toHexString'
        elif func == "id":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "input":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "int":
            if len(args_lst) == 2:
                raise NotImplementedError(f"{func} with a custom base is not supported")
            return f"{args}.toInt"
        elif func == "isinstance":
            obj = args_lst[0]
            cls = args_lst[1]
            return f"{obj}.isInstanceOf[{cls}]"
        elif func == "issubclass":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "iter":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "len":
            return f"{args}.size"
        elif func == "list":
            return f"scala.collection.mutable.Buffer({args}.toSeq: _*)"
        elif func == "locals":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "map":
            func = args_lst[0]
            iterable = args_lst[1]
            if len(args_lst) > 2:
                for it in args_lst[2:]:
                    iterable = f"{iterable}.zip({it})"
                return f"{iterable}.map(({func} _).tupled)"
            else:
                return f"{iterable}.map({func})"
        elif func == "max":
            if len(args_lst) == 1:
                return f"{args}.max"
            else:
                func_str = args_lst[0]
                for arg in args_lst[1:]:
                    func_str = f"{func_str}.max({arg})"
                return func_str
        elif func == "min":
            if len(args_lst) == 1:
                return f"{args}.min"
            else:
                func_str = args_lst[0]
                for arg in args_lst[1:]:
                    func_str = f"{func_str}.min({arg})"
                return func_str
        elif func == "memoryview":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "next":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "oct":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "open":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "ord":
            return f"{args}.charAt(0).toInt"
        elif func == "pow":
            return f"math.pow({args})"
        elif func == "print":
            return f"println({args})"
        elif func == "property":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "range":
            return f"Range({args})"
        elif func == "repr":
            return f"{args}.toString"
        elif func == "reversed":
            return f"{args}.reverse.toBuffer"
        elif func == "round":
            return f"math.round({args})"
        elif func == "set":
            return f"scala.collection.mutable.Set({args}.toSeq: _*)"
        elif func == "setattr":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "slice":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "sorted":
            return f"{args}.sorted.toBuffer"
        elif func == "staticmethod":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "str":
            return f"{args}.toString"
        elif func == "sum":
            return f"{args}.sum"
        elif func == "super":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "tuple":
            return f"({args})"
        elif func == "type":
            return f"{args}.getClass"
        elif func == "vars":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "zip":
            if len(args_lst) == 1:
                raise ValueError(
                    "Cannot zip only 1 iterable because scala does not support 1-tuple."
                )
            func_str = args_lst[0]
            for arg in args_lst[1:]:
                func_str = f"{func_str}.zip({arg})"
            return func_str
        elif func == "__import__":
            raise NotImplementedError(f"{func} is not supported")

        # math library: https://docs.python.org/3/library/math.html
        elif func == "math.comb":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.copysign":
            return f"math.copySign({args})"
        elif func == "math.fabs":
            return f"math.abs({args})"
        elif func == "math.factorial":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.fmod":
            return f"math.floorMod({args})"
        elif func == "math.frexp":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.fsum":
            return f"{args}.sum"
        elif func == "math.gcd":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.isclose":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.isfinite":
            return f"{args}.isFinite"
        elif func == "math.isinf":
            return f"{args}.isInfinite"
        elif func == "math.isnan":
            return f"{args}.isNaN"
        elif func == "math.isqrt":
            return f"math.floor(math.sqrt({args}))"
        elif func == "math.lcm":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.ldexp":
            x, i = args_lst
            return f"({x} * math.pow(2, {i}))"
        elif func == "math.modf":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.nextafter":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.perm":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.prod":
            return f"{args}.product"
        elif func == "math.remainder":
            return f"math.IEEEremainder({args})"
        elif func == "math.trunc":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.exp2":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.log2":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.dist":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.degrees":
            return f"math.toDegrees({args})"
        elif func == "math.radians":
            return f"math.toRadians({args})"
        elif func == "math.acosh":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.asinh":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.atanh":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.erf":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.erfc":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.gamma":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.lgamma":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.pi":
            return "math.Pi"
        elif func == "math.e":
            return "math.E"
        elif func == "math.tau":
            raise NotImplementedError(f"{func} is not supported")
        elif func == "math.inf":
            return "scala.Double.PositiveInfinity"
        elif func == "math.nan":
            return "scala.Double.NaN"

        # otherwise
        else:
            return f"{func}({args})"

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
            op_str = f"math.pow({left}.toDouble, {right}.toDouble)"
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
            op_str = f"math.floorDiv({left}.toLong, {right}.toLong)"
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
        ifs_lst = [self.translate_expr(i) for i in node.ifs]
        if len(ifs_lst) == 0:
            ifs = ""
        else:
            ifs = " && ".join(ifs_lst)
            ifs = f"if ({ifs})"
        c_str = f"{indent}{target} <- {iterr} {ifs}"
        return c_str

    def translate_excepthandler(self, node):
        raise NotImplementedError

    def translate_arguments(self, node):
        if node.kwarg is not None:
            raise NotImplementedError(f"kwargs are not supported:\n{ast.dump(node, indent=2)}")
        vararg_lst = [] if node.vararg is None else [self.translate_arg(node.vararg) + "*"]
        args_lst = [self.translate_arg(arg) for arg in node.args]
        defaults_lst = [self.translate_expr(d) for d in node.defaults]

        argdef_lst = []
        i = len(args_lst) - 1
        j = len(defaults_lst) - 1
        while i >= 0:
            if j >= 0:
                arg = f"{args_lst[i]} = {defaults_lst[j]}"
            else:
                arg = f"{args_lst[i]}"
            argdef_lst.append(arg)
            i -= 1
            j -= 1
        argdef_lst = argdef_lst[::-1]
        return ", ".join(argdef_lst + vararg_lst)

    def translate_arg(self, node):
        annotation = self.translate_annotation(node.annotation)
        return f"{node.arg}: {annotation}"

    def translate_keyword(self, node, indent=""):
        arg = node.arg
        value = self.translate_expr(node.value, indent=indent)
        return f"{arg} = {value}"

    def translate_alias(self, node):
        # only used in import statement
        name = node.name
        asname = node.asname
        if asname is not None:
            alias_str = f"{{{name} => {asname}}}"
        else:
            alias_str = name
        return alias_str

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
        return {"int": "Int", "float": "Double", "bool": "Boolean", "str": "String"}[node.id]


__all__ = ["to_object", "to_str"]
