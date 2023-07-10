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
    z: int
    if x > 3:
        z = 4
    elif x > 5:
        z = 6
    else:
        z = 10
    return z


funs = [addOne, mult6, fun1, fun2, fun3, fun4, fun5, fun6]
bin_op_str = pyala.to_object(*funs, object_name="BinOp")
with open("scala/src/main/scala/BinOp.scala", "w") as fid:
    fid.write("// This file was auto-generated\n\n")
    fid.write(bin_op_str)
