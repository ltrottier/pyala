// This file was auto-generated

object BinOp {
  def addOne(x: Integer) = {
    (x + 1)
  }
  def mult6(x: Integer) = {
    (x * 6)
  }
  def fun1(x: Integer) = {
    scala.collection.mutable.Buffer(x, (x + 1), (x + 2), "c")
  }
  def fun2(x: Integer) = {
    (7  <  8) && (8  >  x) && (x  >  3)
  }
  def fun3(x: Integer) = {
    var z = scala.collection.mutable.Buffer(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    var y = for {
      i <- z if (((i % 2)  ==  0) && ((i % 4)  ==  0))
      j <- z if (((j % 3)  ==  0))
    } yield (i, j)
    y
  }
}