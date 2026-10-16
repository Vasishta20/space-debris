package org.course.spacedebris.rdd

import org.apache.spark.{SparkConf, SparkContext}

/**
  * Single-dataset RDD analysis.
  *
  * The input is the canonical catalog CSV.  The job deliberately
  * uses a small set of fields from that one dataset; it does not read the
  * joined source on D: or a synthetic fixture.
  */
case class CatalogRecord(
    objectId: String,
    category: String,
    periodMin: Double,
    altitudeKm: Double,
    aliases: Seq[String]
)

object RddAnalysis {
  private val HeaderPrefix = "norad_id,epoch,inclination,raan,eccentricity"

  /** Parse one row of the canonical 22-column catalog. */
  def parseLine(line: String): Option[CatalogRecord] = {
    if (line.trim.isEmpty || line.startsWith(HeaderPrefix)) None
    else {
      val fields = line.split(",", -1).map(_.trim)
      if (fields.length != 22 || fields(0).isEmpty || fields(12).isEmpty || fields(11).isEmpty || fields(18).isEmpty) None
      else {
        try {
          val altitude = fields(11).toDouble
          val period = fields(18).toDouble
          if (!finite(altitude) || !finite(period)) None
          else {
            val category = if (fields(12) == "UNKNOWN") "UNK" else fields(12)
            val aliases = Seq(fields(13), fields(10))
              .flatMap(_.split("[\\s-]+").filter(_.nonEmpty))
              .distinct
            Some(CatalogRecord(fields(0), category, period, altitude, aliases))
          }
        } catch {
          case _: NumberFormatException => None
        }
      }
    }
  }

  private def finite(value: Double): Boolean =
    !java.lang.Double.isNaN(value) && !java.lang.Double.isInfinite(value)

  def main(args: Array[String]): Unit = {
    require(args.nonEmpty, "provide the canonical catalog CSV path")
    val input = args(0)
    val requestedPartitions = if (args.length > 1) args(1).toInt else 4
    require(requestedPartitions > 0, "partitions must be positive")

    val conf = new SparkConf()
      .setAppName("SpaceDebrisRddAnalysis")
      .setMaster("local[2]")
      .set("spark.ui.enabled", "false")
      .set("spark.driver.bindAddress", "127.0.0.1")
    val sc = new SparkContext(conf)
    sc.setLogLevel("WARN")

    try {
      val rawLines = sc.textFile(input, minPartitions = requestedPartitions).repartition(requestedPartitions)
      val parsed = rawLines.map(parseLine)
      val valid = parsed
        .flatMap(_.toSeq)
        .filter(record => record.altitudeKm >= 200.0 && record.altitudeKm <= 2000.0)
        .persist()

      // Actions: count, collect, take, and reduce.  The repeated counts
      // demonstrate reuse of the persisted RDD rather than recomputation.
      val rawCount = rawLines.count()
      val validCount = valid.count()
      val categoryCounts = valid.map(record => (record.category, 1)).reduceByKey(_ + _).sortByKey().collect()
      val aliases = valid.flatMap(_.aliases).distinct().sortBy(identity).take(8)
      val totalAltitude = valid.map(_.altitudeKm).reduce(_ + _)

      println(s"input=$input")
      println(s"raw_rows=$rawCount")
      println(s"valid_rows=$validCount")
      println(s"requested_partitions=$requestedPartitions")
      println(s"raw_partitions=${rawLines.getNumPartitions}")
      println(s"valid_partitions=${valid.getNumPartitions}")
      println(s"category_counts=${categoryCounts.mkString(";")}")
      println(s"distinct_aliases=${aliases.mkString("|")}")
      println(f"total_altitude_km=$totalAltitude%.3f")
      println(s"storage_level=${valid.getStorageLevel.description}")
      println(s"lineage=${valid.toDebugString.replace(System.lineSeparator(), "\\n")}")
      println("dag=raw textFile -> repartition -> map(parseLine) -> flatMap(valid rows) -> filter(altitude range) -> persist; branches: map/reduceByKey/sortByKey(category counts), flatMap/distinct/sortBy/take(aliases), map/reduce(total altitude)")
      println("fault_tolerance=RDD lineage records the recomputation plan if a partition is lost; this run does not induce executor or machine failure")
    } finally {
      sc.stop()
    }
  }
}
