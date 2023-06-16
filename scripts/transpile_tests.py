from pyala import pyala


# BinOp
def addOne(x: int):
    return x + 1


def mult6(x: int):
    return x * 6

def fun1(x: int):
    return [x, x+1, x+2, 'c']

def fun2(x: int):
    return 7 < 8 > x > 3

def fun3(x: int):
    z = [1,2,3,4,5,6,7,8,9,10]
    y = [(i,j) for i in z if i % 2 == 0 if i % 4 == 0 for j in z if j % 3 == 0]
    return y

bin_op_str = pyala.to_object(addOne, mult6, fun1, fun2, fun3, object_name="BinOp")
with open("scala/src/main/scala/BinOp.scala", "w") as fid:
    fid.write("// This file was auto-generated\n\n")
    fid.write(bin_op_str)
