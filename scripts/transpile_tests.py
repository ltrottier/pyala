import math

from pyala import pyala


# BinOp
def addOne(x: int):
    return x + 1


def mult6(x: int):
    return x * 6


def fun1(x: int):
    return [x, x + 1, x + 2, "c"]


def fun2(x: int):
    return 7 < 8 > x > 3


def fun3(x: int):
    z = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    y = [(i, j) for i in z if i % 2 == 0 if i % 4 == 0 for j in z if j % 3 == 0]
    return y


def fun4(x: int):
    z = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    return z[2:7:x]


def fun5(x: int):
    y = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    z = {i: i * j + x for i in y if i % 2 == 0 for j in y if j % 3 == 0}
    return z


def fun6(x: int):
    z: int = 0
    if x > 3:
        z = 4
    elif x > 5:
        z = 6
    else:
        z = 10
    return z


def fun7(x: int):
    z: int = 0
    for i, j in [(1, 2), (2, 3), (3, 4)]:
        z = z + i + j
    return z + x


def fun8(x: int):
    i: int = 0
    z: int = 1
    while i < x:
        z *= 2
        i += 1
    return z


def fun9():
    raise ValueError("It just raises")


def fun10(x: float):
    return math.sqrt(x)


def fun11(x: float):
    z: int = 0
    for i in [1, 2, 3, 4, 5, 6]:
        if i == 3:
            pass
        elif i == x:
            z = i
            break
    return z


def fun12(x: int):
    z: float = float(x)
    return f"{z:0.2f}{x:3d}"


def fun13(x: int):
    z: int = 0
    for i in range(10, 100, x):
        z = z + i
    return z


def fun14(*x: int):
    return sum(x)


def fun15(x: int, y: int, *z: int):
    return x + y + sum(z)


def fun16(x: int):
    return chr(x)


def fun17(x: int):
    return bin(x)


def fun18(x: int):
    return frozenset(set(range(1, x)))


def fun19():
    x = [True, True, True]
    y = [True, False, False]
    return all(x), any(y)


def fun20():
    x = [1, 2, 3, 4]
    y = [3, 4, 5]

    def inc(x: int, y: int):
        return x + y + 1

    return list(map(inc, x, y))


def fun21(x: int):
    return max(1, 2, 3, 4, 5, x) + min([-1, -2, -3, -4])


def fun22():
    return ord("€")


funs = [
    addOne,
    mult6,
    fun1,
    fun2,
    fun3,
    fun4,
    fun5,
    fun6,
    fun7,
    fun8,
    fun9,
    fun10,
    fun11,
    fun12,
    fun13,
    fun14,
    fun15,
    fun16,
    fun17,
    fun18,
    fun19,
    fun20,
    fun21,
    fun22,
]
pyala.to_file(*funs, filepath="scala/src/main/scala/BinOp.scala")
