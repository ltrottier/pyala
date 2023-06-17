import scala.reflect.runtime.universe._
import scala.tools.reflect.ToolBox
import java.io.{ObjectInputStream, ObjectOutputStream}
import java.nio.file.{Files, Paths}

import scala.reflect.runtime.universe._
import scala.tools.reflect.ToolBox
import scala.reflect.io.AbstractFile
import java.io.FileOutputStream

object Main extends App {
  def compileAndRun(sourceCode: String): Any = {
    val mirror = runtimeMirror(getClass.getClassLoader)
    val toolbox = mirror.mkToolBox()
    val tree = toolbox.parse(sourceCode)
    val compiledCode = toolbox.compile(tree)
    compiledCode()
  }

  val sourceCode =
    """
        |object Func {
        |   def add(a: Int, b: Int): Int = a + b
        |}
        |Func.add _
    """.stripMargin

  val func = compileAndRun(sourceCode).asInstanceOf[(Int, Int) => Int]

  println(func(2, 3))
  println(func(7, 1))

  def reloadClass(classFile: String, className: String): Class[_] = {
    val classLoader = new ClassLoader(getClass.getClassLoader) {
      def loadClassFromFile(className: String, classFile: String): Class[_] = {
        val bytes = Files.readAllBytes(Paths.get(classFile))
        defineClass(className, bytes, 0, bytes.length)
      }
    }
    classLoader.loadClassFromFile(className, classFile)
  }
  // scalac on file MyClass.scala
  // class MyClass {
  //   def foo(x: Int): Int = x + 1
  // }

  val myClass = reloadClass("/tmp/MyClass.class", "MyClass")
  val method = myClass.getMethod("foo", classOf[Int])
  val instance = myClass.newInstance()
  val result = method.invoke(instance, 5)
  println(result)

  def serializeObject(obj: Any, filePath: String): Unit = {
    val outputStream = new ObjectOutputStream(
      Files.newOutputStream(Paths.get(filePath))
    )
    outputStream.writeObject(obj)
    outputStream.close()
  }

  // Deserialize an object from a file and return it
  def deserializeObject(filePath: String): Any = {
    val inputStream = new ObjectInputStream(
      Files.newInputStream(Paths.get(filePath))
    )
    val obj = inputStream.readObject()
    inputStream.close()
    obj
  }

  // Usage example
  val filePath = "myObject.ser"

  // Serialize the object
  serializeObject(instance, filePath)

  // Deserialize the object
  val deserializedObj = deserializeObject(filePath)

  // Use the deserialized object
  println(deserializedObj)
}
