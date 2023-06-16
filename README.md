# pyala
Python 3.10 to Scala 2.13 Transpiler

> **Warning**
> Project under development. Not available right now. Come back later.

# How to use

```python
import pyala

def foo(x: int):
    return x + 1

scala_source = pyala.to_str(foo)
print(scala_source)
```

# Not Supported

* expr NamedExpr
* expr Lambda
* operator MatMul

# Discrepancies

## operator

### FloorDiv

The return of floor div will always be a scala.Long, even if you use float.

Eg.:
In python: 3.0//2 -> 1.0 (float)
In scala: 3.0//2 -> 1 (Long)

# References

* Python AST: https://docs.python.org/3/library/ast.html
