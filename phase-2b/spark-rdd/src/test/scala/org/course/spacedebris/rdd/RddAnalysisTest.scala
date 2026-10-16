package org.course.spacedebris.rdd

import org.junit.jupiter.api.Assertions._
import org.junit.jupiter.api.Test

class RddAnalysisTest {
  private val valid = "1000,2023-03-23 01:13:39.17568+05:30,32.1412,260.2084,0.0009361,52.8771,307.2581,9.8888978,1.1e-07,0.00030687,65008B,2789.02,DEB,TITAN 3A DEB [TRUSS],US,1965-02-11,,UNKNOWN,145.61784630841265,false,MEO,Other"

  @Test def parsesCanonicalCatalogRow(): Unit = {
    val record = RddAnalysis.parseLine(valid).get
    assertEquals("1000", record.objectId)
    assertEquals("DEB", record.category)
    assertEquals(2789.02, record.altitudeKm, 0.001)
    assertEquals(145.61784630841265, record.periodMin, 0.000001)
    assertTrue(record.aliases.contains("TITAN"))
  }

  @Test def rejectsHeaderMalformedAndNonFiniteRows(): Unit = {
    assertTrue(RddAnalysis.parseLine("norad_id,epoch,inclination,raan,eccentricity").isEmpty)
    assertTrue(RddAnalysis.parseLine(valid.replace(",2789.02,", ",not-a-number,")).isEmpty)
    assertTrue(RddAnalysis.parseLine(valid.replace(",2789.02,", ",NaN,")).isEmpty)
  }
}
