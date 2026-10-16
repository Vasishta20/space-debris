# Spark MLlib conjunction-ranking readiness — 2026-10-15

## Available data

The cleaned Parquet artifact contains 68,129 SATCAT rows with metadata/orbital columns including `OBJECT_TYPE`, `PERIOD`, `INCLINATION`, `APOGEE`, `PERIGEE`, and `RCS`. The project’s bounded screening output contains one candidate record with miss distance and relative velocity. No conjunction outcome, historical event identifier, CDM label, collision/no-collision field, or independent reference miss-distance table is present.

`OBJECT_TYPE` is a catalog category and is already used by the separate PySpark classifier. It is not a collision-risk target. The deterministic distance/relative-velocity prioritization score is derived from the candidate itself and cannot be reused as an independent training label.

## Readiness conclusion

An MLlib conjunction-ranking model is **not ready for defensible supervised training**. The available conjunction sample has one candidate and zero independent outcomes. A train/test split, ranking metric, or calibration result would be scientifically invalid. A reusable unsupervised Spark MLlib exploratory pipeline is implemented in `scripts\pyspark_mllib_exploratory_ranking.py`; it validates real miss-distance/relative-velocity fields and, only when enough real rows exist, can fit `StandardScaler + KMeans` and order rows by distance to a learned feature cluster. That ordering is exploratory feature similarity, not collision likelihood. The current one-row input correctly stops with `status=not_ready_for_fit`; no model was persisted.

## Minimum legitimate training data

At minimum, the project needs many independently recorded conjunction events with stable event IDs, primary/chaser NORAD IDs, TCA in UTC, source orbit products or CDMs, miss distance and units, relative velocity, covariance/uncertainty information where available, object dimensions/mass or consequence features, and an outcome or expert-reviewed action label. Negative/non-event examples need a documented sampling rule. Records must be time-ordered and grouped so an earlier period trains and a later period evaluates, with object/event leakage controls.

Only after those inputs exist would an MLlib design be justified: leakage-safe time split, feature preparation fit on training data, a ranking or binary outcome target defined independently of the heuristic, held-out ranking/classification metrics, calibration assessment if probabilities are produced, and comparison with transparent baselines. The current object-type classifier and deterministic heuristic remain separate artifacts.
