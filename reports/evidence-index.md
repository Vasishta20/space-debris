# Evidence index

| Evidence | Location | Status |
|---|---|---|
| Scala RDD source/build | `phase-2b\spark-rdd` | Verified |
| Latest Scala output | `phase-2b\scala-rdd-output-final.log` | Verified |
| Candidate provenance | `data\screening.json` | Verified |
| Candidate repeat run | `reports\screening-repeat.log` | Verified |
| Parquet round trip | `data\satcat_clean.parquet`, `data\satcat_clean.json` | Verified |
| PostgreSQL migration | `data\postgres-migration.json`, `data\postgres.log` | Verified |
| EDA figures | `reports\eda\*.png` | Verified |
| API/frontend report | `COMPLETION-REPORT.md` | Verified |
| PySpark failure logs | `phase-2b\pyspark-smoke-repro*.log`, `pyspark-smoke-sparkhome-deps.log`, `pyspark-smoke-faulthandler.log`, `pyspark-spark-submit-final.log`, `pyspark-spark-submit-no-driver-python.log`, `pyspark-worker-diagnostic-final.log`, `pyspark-version-diagnostic.log` | Attempted but unresolved; worker still exits with EOF |
| Alternative runtime inspection | `reports\pyspark-alternative-runtime-investigation.md`, `reports\pyspark-wsl-ml.md` | WSL2 setup and compatible runtime verified; native Windows failure remains documented |
| WSL PySpark worker smoke test | `reports\pyspark-wsl-smoke.log`, `scripts\pyspark_wsl_smoke.py` | Verified real worker action and clean Spark stop |
| PySpark ML object-type model | `reports\pyspark-ml-wsl.log`, `data\pyspark_ml_object_type\metrics.json`, `data\pyspark_ml_object_type\model` | Verified; object-type classification only, not collision risk |
| Fresh PySpark reproducibility validation | `reports\pyspark-ml-validation-20261015.log`, `data\pyspark_ml_validation_20261015\metrics.json` | Verified; split distributions, per-class precision/recall/F1, majority baseline, and reload equivalence |
| Candidate prioritization | `scripts\risk_prioritization.py`, `data\screening_prioritized.json`, `tests\test_risk_prioritization.py` | Verified deterministic heuristic; explicitly not collision probability |
| Altitude-shell screening and equivalence | `app\shell_screen.py`, `tests\test_shell_screen.py`, `reports\shell-screen-validation-20261015.json` | Bounded shell-vs-brute-force identity/result match; full-catalog run not claimed |
| Deterministic ranking refresh | `data\screening_prioritized_shell_20261015.json`, `reports\ranking-shell-20261015.log` | Actual candidate ranked with validated components and tie-breaking |
| Final shell regression tests | `reports\python-tests-shell-20261015.log`, `reports\scala-maven-shell-20261015.log` | 22 Python tests and Scala Maven test command exited 0 |
| Historical validation assessment | `reports\historical-validation-20261015.md` | NASA event source identified and preserved; project-specific numerical reproduction remains unverified |
| NASA historical event source | `reports\historical-sources\nasa-iridium-cosmos-event-summary.pdf` | Public NASA event record preserved; numerical SGP4 reproduction remains blocked by missing epoch-specific states |
| MLlib conjunction readiness | `reports\mllib-conjunction-readiness-20261015.md` | No independent labels; reusable exploratory pipeline present but no fit claimed |
| MLlib exploratory pipeline readiness | `scripts\pyspark_mllib_exploratory_ranking.py`, `reports\mllib-exploratory-ranking-20261015.json` | Reusable unsupervised pipeline present; actual one-candidate data correctly refused fit |
| Hive definitions/tests | `hive\queries.hql`, `hive\README.md`, `tests\test_hive_queries.py` | Schema and null-safe rollup unit-tested; execution blocked by absent Hive/runtime/input |
| Cassandra definitions/tests | `cassandra\schema.cql`, `app\cassandra_store.py`, `tests\test_cassandra_store.py` | Adapter and CQL schema unit-tested; live service unavailable |
| Remaining-requirements regression | `reports\python-tests-remaining-requirements-20261015.log`, `reports\scala-maven-remaining-requirements-20261015.log`, `reports\pyspark-wsl-smoke-remaining-requirements-20261015.log` | 30 Python tests, Scala Maven, and WSL smoke passed |
| Shell scalability assessment | `scripts\assess_shell_scalability.py`, `reports\shell-scalability-20261015.json`, `reports\shell-scalability-20261015.log` | Grouped versus epoch-streaming runs matched candidate identities; streaming reduced traced working allocation; catalog figures are arithmetic estimates only |
| Historical/scalability regression | `reports\python-tests-historical-scalability-20261015.log`, `reports\scala-maven-historical-scalability-20261015.log`, `reports\pyspark-wsl-smoke-historical-scalability-20261015.log` | 22 Python tests, Scala Maven tests, and WSL worker smoke passed; Ubuntu terminated afterward |
| Scalable redesign regression | `reports\python-tests-scalable-redesign-20261015.log`, `reports\scala-maven-scalable-redesign-20261015.log`, `reports\pyspark-wsl-smoke-scalable-redesign-20261015.log` | 24 Python tests, Scala Maven tests, and WSL worker smoke passed after streaming refactor |
| Independent-history regression | `reports\python-tests-independent-history-20261015.log`, `reports\scala-maven-independent-history-20261015.log`, `reports\pyspark-wsl-smoke-independent-history-20261015.log` | 24 Python tests, Scala Maven tests, and WSL worker smoke passed |
| Exact Review 3 matrix | `reports\review3-requirements-matrix.md` | Completed against the located Review 3 attachment |
| Presentation deck | `submission\review3-slide-deck.md` | Prepared 12-slide Markdown deck |
| Genuine copied evidence | `submission\evidence\` | Actual logs, JSON, and EDA plots copied; GUI screenshots pending |
| Final WSL smoke rerun | `submission\evidence\pyspark-wsl-smoke-final.log` | Application-level `smoke_status=PASS`; Spark stderr warnings explain wrapper exit code 1 |
| Final Python test rerun | `submission\evidence\python-tests-final.log` | Earlier 14 tests passed; current focused/regression run passes 22/22 under project venv |
| Full joined CSV validation | `reports\joined-dataset-validation-20261015.json`, `submission\evidence\joined-dataset-validation.*` | 29,136,654-row read-only scan, malformed/duplicate/missing/numeric checks, Parquet identifier comparison |
| Scala partition benchmark | `reports\benchmarks\scala-rdd-repeat-partitions-{1,2,4}.log`, copied under `submission\evidence\` | Equivalent six-record fixture results across 1/2/4 partitions; not a distributed speedup claim |
| Rubric/proposal reconciliation | `reports\rubric-proposal-reconciliation.md` | Cassandra, Hive, MLlib, shell bucketing, and historical validation classified as proposal requirements/gaps |
| Fault-tolerance experiment | `phase-2b\fault-tolerance`, `fault-tolerance-local-2-2.log`, `fault-tolerance-final-attempt.log`, `fault-tolerance-experiment-local-cluster.log` | Demonstrated; local task retry/recomputation verified, worker/machine recovery not tested |
| Presentation content | `reports\presentation-outline.md` | Prepared; screenshots not captured |
| Strict final Review 3 audit | `reports\review3-final-submission-audit.md` | PASS/PARTIAL/UNVERIFIED checklist against the attached 15-mark rubric; proposal-only Hive/Cassandra excluded |
| Final project report | `submission\project-report.md` | Complete Markdown report following the rubric section order; team/institution metadata and rendered page count remain to be filled/checked |
| Final 12-slide presentation | `submission\review3-slide-deck.md` | Strict rubric flow with actual dataset, RDD, PySpark metrics, and four chart links |
| Real-data RDD evidence | `submission\evidence\scala-rdd-real-satcat-sample-20261015.log` | 100 source-derived SATCAT sample rows, 66 valid, partitions, transformations, actions, key/value aggregation, lineage, DAG, and cache evidence |
| Final audit regression logs | `reports\python-tests-review3-final-audit-20261015.log`, `reports\scala-maven-review3-final-audit-20261015.log`, `reports\pyspark-wsl-smoke-review3-final-audit-20261015.log`, `reports\frontend-build-review3-final-audit-20261015.log` | Commands and actual outcomes for the strict final audit |
| Rendered final report | `submission\project-report.pdf` | Edge-rendered PDF; 230,717 bytes, 8 pages, 4 embedded chart images; visual/structural checks completed |
| Report render source | `submission\project-report.html`, `scripts\render_project_report.py` | Project-local print HTML generated without installing a renderer |
| Report preview | `submission\project-report-preview.png` | Genuine browser preview used for visual layout inspection |
| Submission identity metadata | `submission\project-report.md`, `submission\review3-slide-deck.md`, root `README.md` | Kireeti / CB.SC.U4CSE23057, 23CSE352 Big Data Analytics, Amrita Vishwa Vidyapeetham; department, additional members, and guide remain placeholders |
| Final submission regression rerun | `reports\python-tests-final-submission-20261016.log`, `reports\scala-maven-final-submission-20261016.log`, `reports\frontend-build-final-submission-20261016.log` | Python 30/30 passed; Scala 2/2 passed with BUILD SUCCESS; frontend Vite production build passed |
| Derived 100k sample | `scripts\sample_joined_100k.py`, `data\joined_object_type_100k.csv`, `data\joined_object_type_100k_metadata.json` | Deterministic reservoir sample: 100,000 rows from 29,136,654 valid source rows; original D: dataset read-only |
| Leakage-controlled 100k PySpark ML | `scripts\pyspark_ml_joined_100k.py`, `data\pyspark_ml_joined_100k\metrics.json`, `reports\joined-100k-model-evaluation-20261016.md`, `reports\pyspark-ml-joined-100k-20261016-rerun.log` | NORAD-ID split, validation tuning, class weighting; test accuracy 0.517706 and macro-F1 0.589657; object-type classification only |
| Modern 100k dashboard | `frontend\src\main.tsx`, `frontend\src\style.css`, `app\main.py` (`/api/catalog-100k/*`) | Real 100k catalog counts, category bars, search, filters, table, charts, and separate close-approach review view; frontend build and API checks passed |
| Full 100k category predictions | `data\pyspark_ml_joined_100k\predictions_csv\`, `scripts\pyspark_ml_joined_100k.py` | 100,000 actual/predicted category rows generated by the trained model; dashboard exposes the predicted category beside the known category |
