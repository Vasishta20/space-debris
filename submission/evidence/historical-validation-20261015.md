# Historical conjunction validation — unresolved

Date: 2026-10-15

The project was searched read-only for historical conjunction records, CDM files, documented reference miss distances, event epochs, or an independent close-approach label. No suitable local record was found. The available evidence consists of:

- the bounded CelesTrak Starlink TLE file at `data\starlink.tle`;
- the project-generated screening output at `data\screening.json`; and
- the deterministic prioritization output derived from that same screening.

These are not independent historical validation records. The candidate at 2026-10-14T05:50:00Z has source TLE lines, NORAD IDs, TEME coordinates, 19.837271672 km miss distance, and 0.216007095 km/s relative velocity, but it has no authoritative reference miss distance or historical event label in the project.

The proposal identifies Space-Track/CDM data as the required authoritative source. A valid comparison needs, at minimum, an event identifier, both object identifiers, event epoch/time scale, reference miss distance and units, the source orbit products or covariance/encounter data, and provenance/access metadata. Space-Track access requires an approved account or an already-provided export; none is present locally. No historical event, label, collision probability, or validation accuracy is claimed.

Status: **Unverified / unresolved**. No propagation comparison was run because the required independent reference inputs are absent.
