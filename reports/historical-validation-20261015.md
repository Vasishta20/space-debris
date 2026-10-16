# Historical conjunction validation — unresolved

Date: 2026-10-15

The project was searched read-only for historical conjunction records, CDM files, documented reference miss distances, event epochs, or an independent close-approach label. No suitable local record was found. A bounded public-source check identified and preserved a NASA technical report as an authoritative historical event reference:

- `reports\historical-sources\nasa-iridium-cosmos-event-summary.pdf`
- Source: NASA NTRS technical report, `https://ntrs.nasa.gov/api/citations/20090032050/downloads/20090032050.pdf`

The report documents the Iridium 33 / Cosmos 2251 event: NORAD 24946 and 22675, TCA 2009-02-10 16:55Z, collision altitude about 788.6 km, and post-event predicted miss-distance values of 223 m and 60 m under different maneuver/ephemeris assumptions. It also reports a 102.5-degree relative approach angle and mean orbital summaries. The two miss-distance values are not interchangeable labels: the report explains that the 60 m result includes the planned Iridium maneuver, while the earlier solution was 223 m.

This is a valid historical event reference, but not a reproducible input set for this project’s SGP4 comparison. It does not provide complete epoch-specific two-object state vectors/TLEs or the maneuver-aware ephemeris required to reproduce the project’s TEME propagation and 50 km threshold calculation. Therefore no numerical comparison was run.

The available project-generated evidence remains:

- the bounded CelesTrak Starlink TLE file at `data\starlink.tle`;
- the project-generated screening output at `data\screening.json`; and
- the deterministic prioritization output derived from that same screening.

These are not independent historical validation records. The candidate at 2026-10-14T05:50:00Z has source TLE lines, NORAD IDs, TEME coordinates, 19.837271672 km miss distance, and 0.216007095 km/s relative velocity, but it has no authoritative reference miss distance or historical event label in the project.

The proposal identifies Space-Track/CDM data as the preferred operational source. A reproducible comparison needs, at minimum, an event identifier, both object identifiers, event epoch/time scale, reference miss distance and units, the source orbit products or covariance/encounter data, and provenance/access metadata. Space-Track access requires an approved account or an already-provided export; none is present locally. No screening accuracy, collision probability, or agreement with the NASA event is claimed.

Status: **Source identified; reproduction unverified / unresolved**. The historical event is genuine and independently documented, but the orbit inputs needed for a defensible project-specific numerical comparison are absent.
