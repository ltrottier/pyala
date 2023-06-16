
object Main extends App {
def foo(x: Integer) = {
  var z = 3.0
  scala.math.floorDiv(x.toLong, z.toLong)
}
  println(foo(16))
}
