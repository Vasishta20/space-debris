# Remaining Review 3 work plan — 2026-10-15

Baseline captured before this pass:

- Root Git status contained the previously documented `.idea/workspace.xml`, `pom.xml`, `PeriodMapper.java`, Hadoop configuration, Docker, metastore, MapReduce, and joined-dataset paths.
- D: joined dataset was 6,046,742,709 bytes with last-write time 2026-09-01 20:49:35.
- Existing shell/streaming, object-type PySpark model, PostgreSQL/SQLite, API, and frontend artifacts were preserved.
- WSL Ubuntu was available with Python 3.12.3 and PySpark 3.5.1; Hive, Cassandra, and cqlsh were absent.

Phased implementation and verification:

1. Hive: added project-local `hive/queries.hql` and README. The schema is for user-supplied historical conjunction/CDM records only, partitioned by altitude shell, with explicit null-safe shell/operator rollups. Hive execution is blocked until an isolated Hive runtime and genuine input are provided.
2. Cassandra: added `cassandra/schema.cql`, README, and an optional `app/cassandra_store.py` adapter. Unit tests use a fake session for validation/upsert/lookup behavior; live integration is blocked because Cassandra/cqlsh are absent and no new runtime was installed.
3. MLlib: added `scripts/pyspark_mllib_exploratory_ranking.py` and readiness tests. The actual one-candidate screening input returns `not_ready_for_fit`; no rows are duplicated, no heuristic labels are used, and no model is claimed.
4. Historical source: preserved the public NASA Iridium/Cosmos event report and documented why it cannot reproduce the project SGP4 result without epoch-specific states/TLEs and maneuver-aware ephemerides. Space-Track acquisition remains user-controlled.
5. Regression: run Python, Scala Maven, WSL smoke, and bounded evidence checks; update all reports and verify D:/Git/process preservation.

Remaining user-controlled prerequisites: a Space-Track/CDM export with event states and provenance; an approved isolated Hive runtime plus validated historical event file; and an approved isolated Cassandra runtime for real write/read tests.
