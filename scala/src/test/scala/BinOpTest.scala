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
    test("fun5") {
        assert(BinOp.fun5(2) === scala.collection.mutable.Map(2 -> 20, 4 -> 38, 6 -> 56, 8 -> 74, 10 -> 92))
    }
    test("fun6") {
        assert(BinOp.fun6(0) === 10)
    }
    test("fun7") {
        assert(BinOp.fun7(4) === 19)
    }
    test("fun8") {
        assert(BinOp.fun8(16) === 65536)
    }
    test("fun9") {
        assertThrows[Exception]{BinOp.fun9()}
    }
    test("fun10") {
        assert(BinOp.fun10(49) === 7)
    }
    test("fun11") {
        assert(BinOp.fun11(5) === 5)
    }
    test("fun12") {
        assert(BinOp.fun12(2) === "2.00  2")
    }
    test("fun13") {
        assert(BinOp.fun13(3) === 1605)
    }
    test("fun14") {
        assert(BinOp.fun14(3,4,5,6,7) === 25)
    }
    test("fun15") {
        assert(BinOp.fun15(3,6,9,12) === 30)
    }
    test("fun16") {
        assert(BinOp.fun16(97) === "a")
    }
    test("fun17") {
        assert(BinOp.fun17(97) === "0b1100001")
    }
    test("fun18") {
        assert(BinOp.fun18(5) === Set(1,2,3,4))
    }
    test("fun19") {
        assert(BinOp.fun19() === (true, true))
    }
    test("fun20") {
        assert(BinOp.fun20() === scala.collection.mutable.Buffer(5,7,9))
    }
    test("fun21") {
        assert(BinOp.fun21(7) === 3)
    }
    test("fun22") {
        assert(BinOp.fun22() === 8364)
    }
}
