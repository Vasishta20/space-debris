# Review 3 requirement-compliance audit

Source rubric: the Review 3 implementation brief in the project attachments, read on 2026-10-14. Statuses are evidence-based: **Verified**, **Partial**, **Blocked**, or **Missing**.

| Requirement | Status | Evidence / gap |
|---|---|---|
| Scala Spark RDD loads orbital records | Verified | External module loads a deterministic orbital fixture; genuine run in `phase-2b/scala-rdd-output-final.log`. It intentionally does not read the 6 GB joined file. |
| At least three meaningful transformations | Verified | `repartition`, `map`, `flatMap`, `filter`, `reduceByKey`, `distinct`, and sorting are implemented and visible in `Review3RddAnalysis.scala`; the canonical catalog run is preserved in `submission/evidence/scala-rdd-review3-catalog-final.log`. |
| At least two actions | Verified | `count`, `collect`, `take`, and `reduce` execute; output is preserved. |
| Key-value RDD operations | Verified | Category pairs, `reduceByKey`, and `sortByKey`. |
| Actual partition count | Verified | Output records 2 partitions before and after repartition. |
| RDD lineage | Verified | `toDebugString` output includes HadoopRDD, shuffle, repartition, map, flatMap, filter, and cached partitions. |
| DAG explanation/inspection | Verified | Job prints a branch explanation tied to the implemented transformations/actions. No Spark UI screenshot is present. |
| Cache/persist demonstration | Verified | Before/after cache actions and cached partitions appear in the actual lineage. |
| Fault-tolerance explanation | Demonstrated | The disposable Scala fixture induced partition 0 failure at attempt 0 under `local[2,2]`, then completed at attempt 1. The final partition sums `(0,1,10);(1,0,26)` total 36, matching the independent baseline. This demonstrates local task retry/recomputation only; worker, executor, and machine recovery were not tested. |
| Input validation and deterministic RDD fixture | Verified | JUnit tests cover malformed numeric, missing category, header, valid records, expected category counts, and altitude sum. |
| TLE/SATCAT validation | Partial | Clean SATCAT schema/count, duplicate rejection, numeric parsing, and missing-value measurements are present. Full joined-file validation is intentionally not run; identifier consistency across TLE/SATCAT is not verified. |
| TLE freshness/ingestion timestamp | Partial | Current TLE source URL and screening timestamp are recorded; no scheduled refresh workflow or offline cache metadata beyond the file is implemented. |
| Orbital attributes and EDA | Verified | Apogee, perigee, inclination, period, RCS, object type and owner are processed; four actual charts and EDA JSON exist. |
| Orbital propagation | Partial | SGP4 propagates 60 real Starlink TLEs at seven ten-minute epochs. No covariance, uncertainty, validation against authoritative ephemerides, or relative velocity is calculated. |
| Candidate screening | Partial | Pairwise SGP4/TEME distance threshold is genuine and bounded at 50 km; the fixed-window run reproducibly records one candidate with source TLE lines, NORAD IDs, UTC epoch, distance, and relative velocity. Shell pruning was equivalent to brute force on 60 objects × 7 epochs, but full-catalog execution is not claimed. It is not a confirmed collision assessment. |
| Altitude-shell bucketing and boundary handling | Partial | Project-local shell screening uses geocentric TEME altitude (`radius - 6378.137 km`), 50 km half-open shells, same/adjacent shell comparisons, canonical pair suppression, and unchanged distance/relative-velocity checks. Synthetic boundary, duplicate, exclusion, and brute-force-equivalence tests pass. The bounded 60-object × 7-epoch comparison found one candidate with identical identity and numeric result to brute force; full-catalog resource/scalability behavior remains unverified. |
| PySpark ML model | Verified | Isolated WSL2 Ubuntu worker smoke test passed on Spark/PySpark 3.5.1 with Python 3.12.3 and Java 11.0.32. A real logistic-regression PySpark ML run completed on 68,129 bounded Parquet rows; metrics and saved model are under `data/pyspark_ml_object_type`. |
| Defensible ML target/features | Verified for object-type task | PySpark and scikit-learn models use real SATCAT `OBJECT_TYPE` labels; neither predicts collision risk. The PySpark feature set excludes identifiers and uses five numeric orbital/catalog fields. |
| PySpark ML split/evaluation/baseline | Verified for object-type task | Seed-42 75/25 split, training-fitted median imputation and label indexing, held-out accuracy 0.663899, macro-F1 0.627583, and class support are recorded in `data/pyspark_ml_object_type/metrics.json`. It is not collision-risk prediction and is not claimed comparable to the different scikit-learn feature pipeline. |
| Parquet analytical storage | Verified boundedly | `scripts/parquet_roundtrip.py` writes and reads 68,129 cleaned SATCAT rows with PyArrow; schema and row count are validated in `data/satcat_clean.json`. |
| Three meaningful visualizations | Verified | Four actual Matplotlib distributions exist: apogee, perigee, inclination, and object type counts. Candidate-count and performance charts are not present. |
| Performance analysis | Partial | Staged grouped-versus-streaming shell measurements are preserved for 60/240/960 objects × 7 epochs. Candidate identities matched; streaming peak traced allocation was lower in all cases (0.06/0.15/0.89 MB versus 0.29/1.07/4.06 MB). These are single-process sample measurements; no distributed or full-catalog claim is made. |
| Candidate prioritization | Partial | `scripts/risk_prioritization.py` now performs finite numeric validation, missing-value rejection, explicit component output, and deterministic ranking tie-breaks. The actual candidate ranks with score 0.657476068 (medium). This remains a transparent physical-feature heuristic, not MLlib and not a collision probability. |
| Spark MLlib conjunction-risk ranking | Partial / proposal gap | A reusable unsupervised StandardScaler + KMeans exploratory pipeline validates physical features, but the actual one-candidate input correctly returns `not_ready_for_fit`. No supervised target, predictive metric, probability, or collision-risk model is claimed. |
| PostgreSQL serving database | Verified boundedly | Official portable PostgreSQL 18.6 binaries run on localhost:55432 without a service; migration counts and representative query are in `data/postgres-migration.json`, and live FastAPI requests returned 200 against PostgreSQL. |
| Cassandra serving layer | Partial / blocked | Project-local CQL schema and optional adapter implement/test bounded object-state upsert and lookup behavior against a fake session. Cassandra/cqlsh are absent, so no live integration is claimed. |
| Hive historical rollups | Partial / blocked | Project-local Hive schema and null-safe shell/operator rollup are unit-tested. Hive is absent from WSL and no genuine historical input was loaded; the original D: Hive file remains untouched. |
| Historical close-approach validation | Unverified | A NASA NTRS report was preserved for Iridium 33/Cosmos 2251 with NORAD IDs, TCA, and maneuver-dependent 223 m/60 m reference values. It lacks complete epoch-specific states/TLEs needed for this SGP4 reproduction, so no numerical comparison was claimed. |
| FastAPI backend | Verified | Live HTTP checks cover health, summary, ingestion, EDA, chart delivery, pagination, object detail, close approaches, models, 404, and 422 behavior. |
| React + TypeScript frontend | Verified | Vite build succeeds; dev server returned HTTP 200; client fetches live API responses and labels scientific limitations. |
| Frontend dashboard requirements | Partial | Summary, freshness, objects, EDA, model metrics, candidate table, loading/error states exist. Explicit data-quality/performance panels are not fully surfaced. |
| Local Windows workflow | Verified with WSL PySpark path | Isolated venv, Maven Scala commands, PowerShell backend/frontend/test scripts, and documented WSL2 PySpark commands exist. Native Windows PySpark remains blocked. |
| Tests and evidence | Partial | Thirty Python tests pass, Scala/JUnit evidence exists, and bounded WSL smoke evidence passes. Genuine logs and plots were copied to `submission/evidence`; GUI screenshots remain pending because no screenshot-capable local browser/desktop tool was available. |

## Database decision

The rubric explicitly names PostgreSQL, so SQLite is not a complete substitute for the target architecture. A portable PostgreSQL 18.6 binary cluster was initialized under C:, used on localhost:55432, migrated from SQLite, verified through the API, and stopped without creating a Windows service. SQLite remains the default fallback.

## Evidence inventory

* Scala source/build: `C:\space-debris-collision-risk-output\phase-2b\spark-rdd`
* Scala output/lineage: `phase-2b\scala-rdd-output-final.log` (the earlier `scala-rdd-output.log` is retained where present)
* Scala tests: `phase-2b\scala-maven-test.log` and `spark-rdd\src\test`
* PySpark reproductions/version diagnostics: `phase-2b\pyspark-smoke-repro*.log`, `pyspark-smoke-sparkhome-deps.log`, `pyspark-smoke-faulthandler.log`, and `pyspark-version-diagnostic.log`
* Fault experiment: `phase-2b\fault-tolerance`, `fault-tolerance-local-2-2.log`, `fault-tolerance-final-attempt.log`, and `fault-tolerance-experiment-local-cluster.log`
* EDA charts: `project\reports\eda\*.png`
* Parquet round trip: `project\data\satcat_clean.parquet` and `satcat_clean.json`
* PostgreSQL migration/API: `project\data\postgres-migration.json` and `postgres.log`
* Backend/frontend verification: `project\COMPLETION-REPORT.md`
* Rubric/proposal reconciliation: `project\reports\rubric-proposal-reconciliation.md`
* Large joined-dataset validation: `project\reports\joined-dataset-validation-20261015.json` and `.log`
* Partition benchmark: `project\reports\benchmarks\scala-rdd-repeat-partitions-{1,2,4}.log`
* Alternative runtime decision: `project\reports\pyspark-alternative-runtime-investigation.md`
* WSL2 PySpark worker/ML evidence: `project\reports\pyspark-wsl-ml.md`, `pyspark-wsl-smoke.log`, `pyspark-ml-wsl.log`, and `data\pyspark_ml_object_type\metrics.json`
* Fresh PySpark validation: `project\reports\pyspark-ml-validation-20261015.log` and `data\pyspark_ml_validation_20261015\metrics.json`
* Candidate prioritization evidence: `project\data\screening_prioritized.json`, `project\scripts\risk_prioritization.py`, and `project\tests\test_risk_prioritization.py`
* Altitude-shell validation: `project\app\shell_screen.py`, `project\tests\test_shell_screen.py`, `project\reports\shell-screen-validation-20261015.json`, and `project\data\screening_prioritized_shell_20261015.json`
* Historical source and MLlib readiness: `project\reports\historical-sources\nasa-iridium-cosmos-event-summary.pdf`, `project\reports\historical-validation-20261015.md`, and `project\reports\mllib-conjunction-readiness-20261015.md`
* Remaining implementation definitions: `project\hive\queries.hql`, `project\cassandra\schema.cql`, `project\app\cassandra_store.py`, and `project\scripts\pyspark_mllib_exploratory_ranking.py`
* Exact requirements matrix: `project\reports\review3-requirements-matrix.md`
* Presentation and copied genuine evidence: `project\submission\review3-slide-deck.md` and `project\submission\evidence\`

