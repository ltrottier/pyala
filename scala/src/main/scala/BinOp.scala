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
  def fun4(x: Integer) = {
    var z = scala.collection.mutable.Buffer(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    Range(2, 7, x).map(z(_))
  }
  def fun5(x: Integer) = {
    var y = scala.collection.mutable.Buffer(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    var z = scala.collection.mutable.Map((for {
      i <- y if (((i % 2)  ==  0))
      j <- y if (((j % 3)  ==  0))
    } yield i -> ((i * j) + x)).toSeq: _*)
    z
  }
  def fun6(x: Integer) = {
    var z: Integer = 0
    if (x  >  3) {
      z = 4
    } else {
      if (x  >  5) {
        z = 6
      } else {
        z = 10
      }
    }
    z
  }
  def fun7(x: Integer) = {
    var z: Integer = 0
    for ((i, j) <- scala.collection.mutable.Buffer((1, 2), (2, 3), (3, 4))) {
      z = ((z + i) + j)
    }
    (z + x)
  }
  def fun8(x: Integer) = {
    var i: Integer = 0
    var z: Integer = 1
    while ((i  <  x)) {
      z = (z * 2)
      i = (i + 1)
    }
    z
  }
  def fun9() = {
    throw new Exception("It just raises")
  }
}
