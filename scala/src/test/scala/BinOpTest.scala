import org.scalatest.funsuite.AnyFunSuite

class BinOpTest extends AnyFunSuite {
    test("addOne") {
        assert(BinOp.addOne(1) === 2)
    }
    test("mult6") {
        assert(BinOp.mult6(4) === 24)
    }
}
