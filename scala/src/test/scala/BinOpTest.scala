import org.scalatest.funsuite.AnyFunSuite

class BinOpTest extends AnyFunSuite {
    test("addOne") {
        assert(BinOp.addOne(1) === 2)
    }
    test("mult6") {
        assert(BinOp.mult6(4) === 24)
    }
    test("fun1") {
        assert(BinOp.fun1(1) === scala.collection.mutable.Seq(1, 2, 3, "c"))
    }
    test("fun2") {
        assert(BinOp.fun2(4) === true)
    }
    test("fun3") {
        assert(BinOp.fun3(4) === scala.collection.mutable.Buffer((4, 3), (4, 6), (4, 9), (8, 3), (8, 6), (8, 9)))
    }
    test("fun4") {
        assert(BinOp.fun4(2) === scala.collection.mutable.Buffer(3, 5, 7))
    }
}
