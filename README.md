# pyala
Python 3.10 to Scala 2.13 Transpiler

> **Warning**
> Project under development. Not available right now. Come back later.

# Tutorial

## How to use pyala

1. Define your python function and add type annotations to its input parameters.
2. Declare new variables with empty annotated assignment to specify their local scope.
3. Use one of `pyala.to_str`, `pyala.to_object` or `pyala.to_file` to transpile your code.

```python
from pyala import pyala

# define your functions
def foo():
    ...

def goo():
    ...

# get the source code of a single function
print(pyala.to_str(foo))

# get the source code of multiple functions bundled in an object
print(pyala.to_object(foo, goo, object_name='Example'))

# save the source code in a file
print(pyala.to_file(foo, goo, filepath='/tmp/Example.scala'))
```

## Examples

```python
def foo():
    y: int
    if x < 0:
        y = x**2
    else:
        y = x * 2
    return y + x
```


# Discrepancies

Here are a list of considerations to take into account due to discrepancies between scala and python.

## Imports

Imports are not supported except for:
1. `import math`

The module `scala.math` is automatically imported and will mimic python built-in functions related to math, and the library `math` itself. This means that this code is valid, even though it uses an import:

```python
import math
def foo(x: float):
    return math.sqrt(x)
```

## Reference types

A python reference cannot change type because scala does not allow it.

For instance, this python code is invalid in scala:
```python
x = 4
x = True
```
because x is defined as a scala.Integer and cannot change to scala.Boolean.

## Local Scope

In python, you can return a variable defined in a local scope. This is not allowed in scala.

For instance, this is valid python code:
```python
def foo():
    if True:
        x = 5
    return x
```

but this is not valid is scala:
```scala
def foo() = {
    if (true) {
        val x = 5
    }
    x
}
```

However, you can access variable defined in a parent scope, like this:
```scala
def foo() = {
    var x: Integer = 0
    if (true) {
        x = 5
    }
    x
}
```

For this reason, pyala requires that you add an annotated assignment for each variable that you want to create:
```python
def foo():
    x: int = 0
    if True:
        x = 5
    return x
```

## Variable function arguments

You cannot assign a new value to a function argument. This code is invalid:
```python
def foo(x: int):
    x = x + 1
    return x
```
You must create a new variable:
```python
def foo(x: int):
    z = x + 1
    return z
```

## F-string

String interpolation (f-string) is typed in scala. This means that this code is invalid:
```python
def foo(x: int):
    return f"{x:0.2f}"
```
You can only using float with "f" format:
```python
def foo(x: int):
    z: float = float(x)
    return f"{z:0.2f}"
```

## *args and **kwargs

First, `**kwargs` are not supported. Second, `*args` must always comes last in the argument list. This means that this code:
```python
def foo(*x: int, z:int = 0):
    return sum(x) - z
```
is transpiled to:
```scala
def foo(z: Int = 0, x: Int*) = {
  (x.sum - z)
}
```
Note the order of the parameters is z then x instead of x then z.

You can call this function correctly in python with `goo(3,4,5,6,z=7)` but it will give a compilation error in scala because the correct call is `goo(7,3,4,5,6)`.

Be extra careful when calling function defined in this way. The order will be correct in python but not in scala.

## operator

### FloorDiv

The return of floor div will always be a scala.Long, even if you use float.

Eg.:
In python: 3.0//2 -> 1.0 (float)
In scala: 3.0//2 -> 1 (Long)

### hex

In python, `hex(-42)` returns `"-0x2a"`, in scala it returns `"0xffffffd6"`.

# References

* Python AST: https://docs.python.org/3/library/ast.html
* Built-in Functions: https://docs.python.org/3/library/functions.html
* Math library: https://docs.python.org/3/library/math.html


# Not Supported

## expr NamedExpr
## Lambda
Lambda expressions are not supported:
```python
lambda x: x +1
```
## operator MatMul
## for loop with continue
## async
The keyword `async` is not supported
## complex
