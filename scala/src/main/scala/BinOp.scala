// This file was auto-generated
import scala.util.control.Breaks._


object BinOp {
  def addOne(x: Int) = {
    (x + 1)
  }
  def mult6(x: Int) = {
    (x * 6)
  }
  def fun1(x: Int) = {
    scala.collection.mutable.Buffer(x, (x + 1), (x + 2), "c")
  }
  def fun2(x: Int) = {
    (7  <  8) && (8  >  x) && (x  >  3)
  }
  def fun3(x: Int) = {
    var z = scala.collection.mutable.Buffer(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    var y = for {
      i <- z if (((i % 2)  ==  0) && ((i % 4)  ==  0))
      j <- z if (((j % 3)  ==  0))
    } yield (i, j)
    y
  }
  def fun4(x: Int) = {
    var z = scala.collection.mutable.Buffer(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    Range(2, 7, x).map(z(_))
  }
  def fun5(x: Int) = {
    var y = scala.collection.mutable.Buffer(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    var z = scala.collection.mutable.Map((for {
      i <- y if (((i % 2)  ==  0))
      j <- y if (((j % 3)  ==  0))
    } yield i -> ((i * j) + x)).toSeq: _*)
    z
  }
  def fun6(x: Int) = {
    var z: Int = 0
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
  def fun7(x: Int) = {
    var z: Int = 0
    breakable{for ((i, j) <- scala.collection.mutable.Buffer((1, 2), (2, 3), (3, 4))) {
      z = ((z + i) + j)
    }}
    (z + x)
  }
  def fun8(x: Int) = {
    var i: Int = 0
    var z: Int = 1
    breakable{while ((i  <  x)) {
      z = (z * 2)
      i = (i + 1)
    }}
    z
  }
  def fun9() = {
    throw new Exception("It just raises")
  }
  def fun10(x: Double) = {
    import scala.math
    math.sqrt(x)
  }
  def fun11(x: Double) = {
    var z: Int = 0
    breakable{for (i <- scala.collection.mutable.Buffer(1, 2, 3, 4, 5, 6)) {
      if (i  ==  3) {
        ()
      } else {
        if (i  ==  x) {
          z = i
          break
        } else {

        }
      }
    }}
    z
  }
  def fun12(x: Int) = {
    var z: Double = x.toDouble
    f"$z%.2f" + f"$x%3d"
  }
  def fun13(x: Int) = {
    var z: Int = 0
    breakable{for (i <- Range(10, 100, x)) {
      z = (z + i)
    }}
    z
  }
  def fun14(x: Int*) = {
    x.sum
  }
  def fun15(x: Int, y: Int, z: Int*) = {
    ((x + y) + z.sum)
  }
}
