from pyala import pyala


# BinOp
def addOne(x: int):
    return x + 1


def mult6(x: int):
    return x * 6


bin_op_str = pyala.to_object(addOne, mult6, object_name="BinOp")
with open("scala/src/main/scala/BinOp.scala", "w") as fid:
    fid.write("// This file was auto-generated\n\n")
    fid.write(bin_op_str)
