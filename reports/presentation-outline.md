# Review 3 presentation outline — observed evidence only

## Slide 1 — Problem and scope

Local space-object catalog analytics with bounded TLE propagation and candidate screening. The system does not claim collision probabilities or confirmed collisions.

## Slide 2 — Safe architecture

Scala/Spark RDD fixture → bounded Python analytics → Parquet/SQLite/PostgreSQL serving → FastAPI → React/TypeScript. The original Hadoop repository and 6 GB joined input remain preserved on D:.

## Slide 3 — RDD evidence

Use `phase-2b\scala-rdd-output-latest.log`: 2 partitions, 6 valid cached records, category counts `(DEB,2);(PAY,3);(R/B,1)`, total altitude `3245.0 km`, actual `toDebugString` lineage, and the printed DAG explanation. The Scala Maven test exit code was 0.

## Slide 4 — Data quality and EDA

Use `reports\eda\*.png` and `reports\eda\eda.json`: 68,129 cleaned SATCAT rows loaded, 0 rejected; object types DEB 34,568, PAY 26,830, R/B 6,571, UNK 160. Charts are actual apogee, perigee, inclination, and object-type distributions.

## Slide 5 — Orbital screening

Use `data\screening.json`: 60 current Starlink TLEs, seven fixed UTC epochs at ten-minute intervals, SGP4 TEME coordinates, 50 km threshold, and one candidate: NORAD 45185/45235 at 19.837 km and 0.216 km/s relative velocity. This is a screening candidate, not a collision.

## Slide 6 — ML limitations

The verified WSL2 PySpark model predicts SATCAT `OBJECT_TYPE` with accuracy 0.663899 and macro-F1 0.627583; majority baseline accuracy is 0.511753 and macro-F1 0.169258. It does not predict collision risk. Native Windows PySpark remains blocked, while isolated WSL2 execution is verified.

## Slide 7 — Serving and UI

SQLite and portable PostgreSQL both have verified bounded data. FastAPI live requests passed on both backends. React production build passed and uses live API responses for summary, objects, EDA, model metrics, and candidates.

## Slide 8 — Reproducibility and gaps

Use `reports\performance-analysis.md`, `reports\review3-requirements-matrix.md`, `data\pyspark_ml_validation_20261015\metrics.json`, and the copied evidence. Remaining gaps: full joined-file validation, uncertainty-aware conjunction assessment, distributed performance experiments, and GUI screenshots. These are explicitly not claimed as complete.
