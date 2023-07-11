lazy val root = (project in file(".")).
  settings(
    inThisBuild(List(
      organization := "ch.epfl.scala",
      scalaVersion := "2.13.8"
    )),
    name := "pyala",
    version := "1.0"
  )

libraryDependencies += "org.scalatest" %% "scalatest" % "3.2.16" % Test
libraryDependencies += "org.scala-lang" % "scala-reflect" % "2.13.8"
libraryDependencies += "org.scala-lang" % "scala-compiler" % "2.13.8"
