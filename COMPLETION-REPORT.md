# Backend completion report — external C: workspace

## Remaining requirements implementation — 2026-10-15

Added project-local Hive definitions in `hive\queries.hql` and `hive\README.md` for independently sourced historical conjunction/CDM records, partitioned by altitude shell with null-safe operator rollups. Added schema/query tests. Hive execution remains blocked because WSL has no Hive command and no genuine historical event file is available; the original D: Hive file was not changed.

Added Cassandra readiness artifacts: `cassandra\schema.cql`, `cassandra\README.md`, and the optional `app\cassandra_store.py` adapter keyed by `(object_id, time_bucket, epoch_utc)`. Fake-session tests cover validation, upsert, lookup, and unavailable/invalid input behavior. No Cassandra/cqlsh runtime or live integration was claimed.

Added `scripts\pyspark_mllib_exploratory_ranking.py`. It validates real miss-distance and relative-velocity fields and contains a WSL Spark MLlib `StandardScaler + KMeans` exploratory path for sufficiently sized real inputs. The actual screening input has one candidate, so the run returned `status=not_ready_for_fit`; no rows were duplicated, no heuristic labels were used, and no predictive metric or collision probability was produced. The full Python suite now passes 30/30; Scala Maven and WSL smoke also pass.

## Altitude-shell and ranking implementation update — 2026-10-15

Added project-local `app\shell_screen.py` and deterministic tests. Shells use geocentric altitude from propagated TEME position (`radius - 6378.137 km`), width 50 km, half-open boundaries with exact boundaries assigned to the higher shell, and same/adjacent-shell comparisons. Canonical object/epoch keys suppress duplicate emissions while the original inclusive distance threshold and relative-velocity calculation remain authoritative.

The bounded 60-object × 7-epoch validation processed 420 states in 0.019141 seconds. Shell screening and the independent brute-force reference each found the same single candidate: STARLINK-1216/NORAD 45185 and STARLINK-1246/NORAD 45235 at 2026-10-14T05:50:00Z, 19.837271672 km separation and 0.216007095 km/s relative velocity. Identity and numeric result comparisons passed. This is bounded correctness evidence, not a full-catalog performance claim.

`risk_prioritization.py` now rejects missing/non-finite values, exposes distance/velocity components, and applies deterministic tie-breaking. The actual candidate was ranked with score 0.657476068 (medium). It remains a transparent dimensionless prioritization heuristic, not a collision probability and not Spark MLlib. Evidence is in `reports\shell-screen-validation-20261015.json`, `data\screening_prioritized_shell_20261015.json`, and `reports\ranking-shell-20261015.log`.

The verified Python suite now passes 22/22 under `project\.venv`. The native system-Python invocation remains unable to import `sgp4`; no installation was attempted. Full-catalog shell execution, historical conjunction validation, and proposal-required MLlib conjunction ranking remain unverified or incomplete.

## Historical validation and scalability assessment — 2026-10-15

No independent historical conjunction record was found in the project files. The available CelesTrak TLEs and project-generated candidate output do not provide a reference miss distance or independent event label. Historical validation therefore remains unverified. The minimum required next input is an approved Space-Track/CDM export containing event epoch/time scale, both object identifiers, reference miss distance and units, orbit products or encounter data, and provenance.

A bounded shell scalability assessment used only the existing C: Parquet altitude values to generate local deterministic fixtures. Grouped legacy versus epoch-streaming runtimes for 60/240/960 objects across seven epochs were 0.0192/0.0163, 0.1646/0.1489, and 2.9639/3.2356 seconds; candidate identities matched in every case. Shell comparisons were 261/5,416/114,990 per epoch versus 1,770/28,680/460,320 brute-force pairs. Peak traced allocations legacy/streaming were 0.29/0.06, 1.07/0.15, and 4.06/0.89 MB. For the 68,129-object catalog, arithmetic estimates are 476,903 states and 16,245,223,792 brute-force pair evaluations across seven epochs. No full-catalog job was run. Streaming bounds the working set to one epoch but has no spill or distributed partitioning, so full-catalog scalability remains partial.

The 2026-10-15 regression run passed 22 Python tests, Scala Maven tests, and the existing WSL2 PySpark smoke test (`Spark/PySpark 3.5.1`, Java 11.0.32, Python 3.12.3, two partitions, deterministic result, `smoke_status=PASS`). Ubuntu was terminated after the bounded run. The cleaned Parquet schema contains SATCAT metadata/orbital fields and `OBJECT_TYPE`, but no conjunction outcome, event, miss-distance, or collision label; therefore the proposal-required MLlib conjunction-ranking model remains unsupported by available data.

## Streaming shell redesign — 2026-10-15

`app\shell_screen.py` now provides `screen_epoch_states` and `screen_states_streaming`. The streaming API requires strictly increasing epoch groups, deduplicates within each epoch, compares each same-shell pair once and each adjacent-shell pair once, and releases the epoch working set before consuming the next epoch. The compatibility `screen_states` API remains available for existing callers and groups all supplied epochs.

A concrete correctness defect was fixed: pair deduplication no longer suppresses the same valid object pair at later epochs. New tests cover same-pair multi-epoch preservation and epoch-order validation. The full Python suite passes 24/24, Scala Maven tests pass, and the WSL2 PySpark smoke test passes after the refactor. No full-catalog job was launched.

## Independent historical source and MLlib readiness — 2026-10-15

The public NASA NTRS report `reports\historical-sources\nasa-iridium-cosmos-event-summary.pdf` was preserved as an independent historical event source. It documents Iridium 33/NORAD 24946 and Cosmos 2251/NORAD 22675 at TCA 2009-02-10 16:55Z, with maneuver-dependent post-event predicted miss distances of 223 m and 60 m. The report does not provide complete epoch-specific two-object states/TLEs and maneuver-aware ephemerides, so this project did not claim a numerical SGP4 reproduction or validation accuracy. Details and the exact blocker are in `reports\historical-validation-20261015.md`.

The cleaned Parquet data contains 68,129 SATCAT rows and `OBJECT_TYPE`, but no independent conjunction outcomes, event IDs, CDMs, reference miss distances, or collision labels. The bounded screening contains one candidate only. `reports\mllib-conjunction-readiness-20261015.md` documents why an MLlib conjunction-ranking model is not defensibly trainable and specifies the minimum labeled, time-stamped data required. The object-type classifier and deterministic prioritization heuristic remain separate.

Date: 2026-10-14. Scope: a safe, bounded backend implementation and Review 3 audit outside the original repository.

## Safety and workspace

All new files are under `C:\space-debris-collision-risk-output\project`. The project currently occupies approximately 0.401 GB, including its isolated Python virtual environment. C: had 157,225,824,256 bytes free at the final check (about 146.4 GiB). D: remains full and was not written. The existing joined dataset remains at 6,046,742,709 bytes with the previously observed timestamp. It was not copied, moved, transformed, or opened by the new pipeline.

The root Git status was rechecked and is unchanged: the pre-existing modifications to `.idea/workspace.xml`, `pom.xml`, and `PeriodMapper.java`, plus the previously documented untracked Hadoop configuration, Docker, metastore, Java MapReduce, and joined-dataset paths remain untouched. No root source, POM, or dataset was edited.

## Environment actually used

The process-local interpreter is Python 3.12.0 in `project\.venv`. Installed there for this isolated workspace: FastAPI 0.143.0, Uvicorn 0.54.0, NumPy 2.5.4, pandas 3.0.6, scikit-learn 1.9.1, Matplotlib 3.11.2, sgp4 2.27, PyArrow 26.0.0, psycopg 3.3.6, httpx 0.28.1, and pytest 8.4.2. No global PATH, JAVA_HOME, registry, Docker, or WSL setting was changed.

The Scala Spark RDD demonstration remains in `phase-2b\spark-rdd` and is verified as documented in the Phase 2B report. The PySpark import/version check succeeded, but the Python worker action still fails on this Windows host with an EOF/crash; therefore no PySpark result or PySpark ML result is claimed.

## Actual bounded results

* SATCAT ingest read `D:\Projects\space-debris-collision-risk\data\raw\satcat_clean.csv` only: 68,129 rows seen, 68,129 loaded, 0 rejected. This is the small cleaned SATCAT file, not the 6 GB joined file.
* Object types: DEB 34,568; PAY 26,830; R/B 6,571; UNK 160.
* Mean apogee: 3,512.242 km; mean perigee: 1,683.829 km.
* The classifier is a reproducible scikit-learn logistic-regression baseline predicting SATCAT `OBJECT_TYPE`, using orbital and metadata fields. It is not a collision label, collision probability, or risk model. On a stratified 25% holdout with random state 42: accuracy 0.570598 and macro-F1 0.427990.
* EDA generated `reports\eda\*.png` and `reports\eda\eda.json`.
* The latest fixed-window SGP4 screening used 60 actual Starlink TLEs from the recorded CelesTrak URL, seven UTC epochs at ten-minute intervals, SGP4 TEME coordinates, and a 50 km pairwise threshold. It found 1 candidate: NORAD 45185/45235 at 2026-10-14T05:50:00Z, 19.837271672 km separation, and 0.216007095 km/s relative velocity. A repeat run reproduced the same values. These are bounded screening candidates, not confirmed collisions or risk probabilities.
* SQLite persistence is at `data\analytics.sqlite3`. A bounded Parquet write/read round trip also passed for 68,129 rows with schema validation. A portable PostgreSQL 18.6 cluster on localhost:55432 was initialized under C:, migrated from SQLite, and verified with 68,129 objects plus representative API queries; it was stopped after testing.
* Eleven Python unittest cases pass under `python -m unittest discover -s tests -v`, including API, candidate-screening, and Parquet checks. Pytest collection is blocked by the host-level `C:\Users\dsvas\AppData\Local\Programs\Python\Python312\py.py` shadowing pytest's `py` compatibility module; this is recorded rather than hidden.

## Verification update

The repeatable pipeline was rerun successfully with the same counts and metrics. Eleven unittest cases now pass, covering API behavior, candidate identity/time/units/thresholds, Parquet round-trip evidence, catalog schema/count, TLE propagation, and screening evidence. Live HTTP requests against Uvicorn returned the expected results: `/health`, `/api/summary`, `/api/ingestion`, `/api/eda`, `/api/eda/apogee_hist.png`, `/api/objects`, `/api/objects/1`, `/api/close-approaches`, and `/api/models` returned 200; `/api/objects/999999` returned 404; and `/api/objects?limit=0` returned 422. The PostgreSQL-backed `/health`, `/api/summary`, `/api/objects`, `/api/objects/1`, `/api/models`, and `/api/close-approaches` requests also returned 200. The React/Vite development server returned HTTP 200, and `npm run build` completed successfully with Vite 8.3.4, Node 24.14.0, and npm 10.9.5.

The frontend is at `frontend/`. It uses live FastAPI responses for summary cards, freshness, object pagination/filtering, EDA chart images, model metrics, and explicit scientific caveats. It contains no mock result values. PostgreSQL is implemented as an optional portable local backend under `tools\postgresql-18.6`; SQLite remains the default fallback.

The formal rubric audit is `reports\review3-compliance-audit.md`; measured bounded stage timings are in `reports\performance-analysis.md`.

The latest pipeline run completed successfully with 68,129 SATCAT rows loaded, 0 rejected, the same object-type metrics, and 1 bounded SGP4 candidate with complete source-TLE provenance. The latest Scala Maven test completed with exit code 0 and the RDD executable completed with exit code 0, again reporting 2 partitions, 6 valid cached records, category counts `(DEB,2);(PAY,3);(R/B,1)`, total altitude `3245.0 km`, actual lineage, and the honest non-induced fault-tolerance statement. Eleven Python unittest cases pass, the Parquet round trip passes, the PostgreSQL migration/API checks pass, and the frontend production build passes.

The final native Windows PySpark attempt used the corrected `SPARK_HOME=<runtime>\deps` setting. The version diagnostic recorded Java 17.0.20.1, Python 3.12.0, Spark 3.5.1, and PySpark 3.5.1. The gateway launched, but the minimal DataFrame worker action failed with `SparkException: Python worker exited unexpectedly (crashed)` caused by `java.io.EOFException`; the complete logs are `phase-2b\pyspark-smoke-sparkhome-deps.log` and `phase-2b\pyspark-smoke-faulthandler.log`. A bounded WSL2 Ubuntu probe did not return within 10 seconds, so no WSL installation/configuration or migration was attempted. PySpark ML remains blocked.

The final process diagnostic captured the venv driver executable, effective `SPARK_HOME`, `PYSPARK_PYTHON`, `PYTHONPATH`, Java 17, Spark/PySpark 3.5.1, and the Java launch command. The spawned worker process still resolved to the global `C:\Users\dsvas\AppData\Local\Programs\Python\Python312\python.exe` even after executor-environment propagation and venv-PATH correction. The direct Python launch and `spark-submit.cmd` launch both reproduced the same worker EOF. This identifies a Windows process-launch/interpreter-resolution failure, but not the lower-level reason that the worker exits; no further retries are justified in this sprint.

The final controlled hypothesis test unset `PYSPARK_DRIVER_PYTHON` for a direct `spark-submit.cmd --master local[2]` launch. The gateway and Spark driver started, but the minimal task again failed with `Python worker exited unexpectedly (crashed)` and `EOFException`. This hypothesis is therefore rejected; PySpark remains unresolved.

The alternative-runtime inspection found an installed WSL2 Ubuntu distribution, but it has Python 3.12.3, Java 11, no pip, and no `spark-submit`. Docker CLI 29.1.3 is present, but its daemon is unavailable. Python 3.11 was not found in the inspected local installations. No WSL, Docker, Python, Java, or Spark installation was attempted. The detailed decision is `reports\pyspark-alternative-runtime-investigation.md`.

A separate disposable Scala fault fixture was added under `phase-2b\fault-tolerance`. The original `local[2]` configuration aborted after one failure. The evidence-based `local[2,2]` master URL retry configuration then succeeded: partition 0 failed at attempt 0, succeeded at attempt 1, and the final partition sums were `(0,1,10);(1,0,26)` with total 36 matching the independent baseline. This demonstrates local task retry/recomputation only; it does not demonstrate worker, executor, or machine recovery. The bounded `local-cluster[2,1,1024]` attempt remains incomplete.

## Exact commands

```powershell
$root = 'C:\space-debris-collision-risk-output\project'
$py = "$root\.venv\Scripts\python.exe"
& $py "$root\scripts\run_pipeline.py"
& $py "$root\scripts\parquet_roundtrip.py" 'D:\Projects\space-debris-collision-risk\data\raw\satcat_clean.csv' "$root\data\satcat_clean.parquet"
& $py -m unittest discover -s "$root\tests" -v
& $py -m uvicorn app.main:app --app-dir $root --host 127.0.0.1 --port 8000

# Final bounded PySpark diagnostic; writes only C: logs and stops after the child exits.
& 'C:\space-debris-collision-risk-output\phase-2b\capture-pyspark-worker-diagnostic.ps1'
& 'C:\space-debris-collision-risk-output\phase-2b\pyspark-runtime\pyspark-3.5.1\deps\bin\spark-submit.cmd' --master 'local[2]' 'C:\space-debris-collision-risk-output\phase-2b\spark-rdd\pyspark_smoke.py'

# Disposable fault fixture; uses only eight in-memory integers and C: marker/log files.
$ft = 'C:\space-debris-collision-risk-output\phase-2b\fault-tolerance'
$env:JAVA_HOME = 'C:\space-debris-collision-risk-output\tools\jdk-17.0.20.1+1'
$env:MAVEN_OPTS = '--add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-exports=java.base/sun.security.action=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED --add-opens=java.base/java.lang.invoke=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED'
mvn -f "$ft\pom.xml" "-Dmaven.repo.local=C:\space-debris-collision-risk-output\phase-2b\maven-cache" compile exec:java "-Dexec.args=$ft\fault-recovery-marker.txt" '-Dexec.cleanupDaemonThreads=false'

# Retry-enabled local master; this is the verified recovery experiment.
mvn -f "$ft\pom.xml" "-Dmaven.repo.local=C:\space-debris-collision-risk-output\phase-2b\maven-cache" compile exec:java "-Dexec.args=$ft\fault-recovery-marker.txt local[2,2]" '-Dexec.cleanupDaemonThreads=false'

# PostgreSQL is portable/local only; start it before migration/API verification.
$pg = "$root\tools\postgresql-18.6\pgsql"
$pgdata = "$root\data\postgres"
& "$pg\bin\pg_ctl.exe" -D $pgdata -l "$root\data\postgres.log" -o '"-p 55432"' start
$env:DATABASE_URL = 'postgresql://postgres@127.0.0.1:55432/postgres'
& $py "$root\scripts\postgres_migrate.py"
& $py -m uvicorn app.main:app --app-dir $root --host 127.0.0.1 --port 8001
& "$pg\bin\pg_ctl.exe" -D $pgdata stop -m fast
```

The pipeline creates only bounded reports, plots, a SQLite database, a current TLE sample, and JSON evidence under C:. It does not start Docker, install PostgreSQL, run Spark against the large dataset, or change the original Maven project.

## Remaining limitations and next steps

1. PySpark ML remains not implemented. A future approved environment setup must provide a working PySpark worker—likely by installing compatible packages in WSL2 or another isolated runtime—before implementing the object-type classifier.
2. PostgreSQL is now available as an intentionally provisioned portable local backend and has passed bounded migration/API checks; SQLite remains the default fallback. A production PostgreSQL deployment, backup policy, and operational hardening are outside this sprint.
3. Use validated time-tagged TLE/OMM sources, covariance, encounter geometry, and uncertainty propagation before calling results collision risk. The current 50 km screen is intentionally not a probability estimate.
4. Keep the external C: workspace separate until D: has safe capacity and an explicit integration review. Integrate file-by-file, never by overwriting the existing empty scaffold or root project changes.

5. PySpark remains partial. The recorded native Windows failure is a real Python worker crash (`SparkException` with `EOFException`) during a DataFrame action under the extracted Spark 3.5.1/PySpark 3.5.1 runtime and Python 3.12. A read-only WSL2 environment probe did not return within the command timeout; no WSL package installation, migration, or configuration change was performed. PySpark ML is therefore not claimed.

6. Final integrity check on 2026-10-14: C: had 141,257,285,632 bytes free (131.5 GiB); D: had 0 bytes free; the joined D: dataset remained 6,046,742,709 bytes with timestamp 2026-09-01 20:49:35; WSL Ubuntu and Docker remained stopped; no Spark or fault-fixture process remained after excluding the diagnostic PowerShell process itself; and root Git status still contained only the pre-existing modified/untracked paths documented by Phase 1. No D: file was written.

7. Candidate provenance correction: the earlier two-candidate JSON did not preserve source TLE lines or pair identity, so those historical pairs cannot be independently reconstructed. The current fixed-window evidence corrects that deficiency and reports one reproducible candidate with source lines, NORAD IDs, UTC time, TEME frame, distance, and relative velocity.

8. Fault experiment evidence: `phase-2b\fault-tolerance-local-2-2.log` records the deterministic failure at attempt 0, successful retry at attempt 1, baseline/recovered sum 36, and `correct=true`. This demonstrates local task retry/recomputation only; no separate-executor, worker, or machine recovery is claimed. The earlier `local[2]` abort and incomplete local-cluster logs remain preserved.

9. Final diagnostic integrity check: no Spark/PySpark process remained after the bounded tests. The only application-code change in this pass was the project-local smoke-test interpreter propagation/PATH correction, which did not resolve the worker failure; `pyspark_smoke.py.review3-original.py` preserves the prior version. The final `spark-submit` evidence is `phase-2b\pyspark-spark-submit-no-driver-python.log`.

## WSL2 PySpark recovery update — 2026-10-15

The approved alternative-runtime investigation was completed in the existing Ubuntu WSL2 distribution without changing Windows global configuration, D:, Docker, or the original Hadoop project. Preflight observed Ubuntu 24.04.3 LTS/x86_64, WSL2 kernel 6.6.87.2, Python 3.12.3, Java 11.0.32, 20 CPUs, 7.6 GiB RAM, 943 GiB free in the WSL filesystem, and approximately 131.69 GB free on C:. The C: mounted venv install stalled, so the dependency venv was placed at `/home/dsvasi/pyspark-wsl-venv`; all scripts, logs, reports, metrics, and model artifacts remain under this project root.

Only Ubuntu `python3-pip`/`python3-venv` and project-runtime packages PySpark 3.5.1, NumPy 1.26.4, and setuptools 69.5.1 were added. The real worker smoke test passed with Spark/PySpark 3.5.1, Java 11.0.32, Python worker `/usr/bin/python3`, two partitions, deterministic result `[2,4,6,8,10,12,14,16]`, and `smoke_status=PASS`. Evidence: `scripts\pyspark_wsl_smoke.py` and `reports\pyspark-wsl-smoke.log`.

The PySpark ML object-type classifier then completed against the existing bounded `data\satcat_clean.parquet` artifact: 68,129 rows, features `PERIOD`, `INCLINATION`, `APOGEE`, `PERIGEE`, `RCS`, target `OBJECT_TYPE`, seed 42, train/test 51,027/17,102, accuracy 0.663899, macro-F1 0.627583. The model and metrics are under `data\pyspark_ml_object_type`; detailed evidence is `reports\pyspark-wsl-ml.md` and `reports\pyspark-ml-wsl.log`. This is object-type classification only; no collision labels or collision probabilities are claimed.

The original native Windows PySpark EOF/worker crash remains a Windows-runtime limitation; the working WSL2 runtime is now the documented launch path. A future Windows-native repair is not required for the verified WSL2 result.

Final recovery-sprint checks on 2026-10-15: the saved PySpark model reloaded from `data\pyspark_ml_object_type\model` and transformed a fresh row (`reloaded_stages=4`, `reload_rows=1`); the existing Python suite passed 11/11; and `mvn -f phase-2b\spark-rdd\pom.xml test` passed 2/2 Scala tests. Ubuntu was terminated after the tests and no Spark/PySpark process remained. C: had 146,934,755,328 bytes free; D: had 0 bytes free. The joined dataset remained 6,046,742,709 bytes with last-write time 2026-09-01 20:49:35 +05:30. Git status remained exactly the pre-existing modified/untracked set listed above.

WSL launch commands:

```powershell
wsl.exe -d Ubuntu -- /home/dsvasi/pyspark-wsl-venv/bin/python /mnt/c/space-debris-collision-risk-output/project/scripts/pyspark_wsl_smoke.py
wsl.exe -d Ubuntu -- /home/dsvasi/pyspark-wsl-venv/bin/python /mnt/c/space-debris-collision-risk-output/project/scripts/pyspark_ml_object_type.py --input /mnt/c/space-debris-collision-risk-output/project/data/satcat_clean.parquet --output /mnt/c/space-debris-collision-risk-output/project/data/pyspark_ml_object_type
```

## Full Review 3 completion sprint update — 2026-10-15

The exact Review 3 implementation brief was located at `C:\Users\dsvas\.codex\attachments\8c7f22d7-f56d-4191-a2ae-4bb3880daf47\Pasted text.txt`. The requirement-by-requirement matrix is `reports\review3-requirements-matrix.md`; it records completed, partial, missing, and unverified requirements without treating source existence as execution proof.

A fresh validation run used a new output directory, `data\pyspark_ml_validation_20261015`, and did not overwrite the prior model. It reproduced 68,129 rows, a seed-42 51,027/17,102 split, accuracy `0.6638989592`, macro-F1 `0.6275827871`, per-class precision/recall/F1, and class counts. The majority-class baseline was DEB with accuracy `0.5117530113` and macro-F1 `0.1692581419`. Reloading the saved PipelineModel gave `reload_prediction_equivalence=true`. This remains SATCAT object-type classification, not collision-risk prediction.

Because no defensible collision labels exist, `scripts\risk_prioritization.py` now generates a separate deterministic prioritization score from actual candidate miss distance and relative velocity. The candidate scored `0.657476068` (medium); the output explicitly says it is not a collision probability. Three edge-case tests were added. The score is not connected to the API/frontend because presenting it as calibrated risk would be scientifically misleading.

The Python regression suite now passes 14/14. Genuine evidence was copied under `submission\evidence\`, including four EDA plots, screening/provenance JSON, RDD and retry logs, WSL smoke/ML logs, validation metrics, and the Python test log. A 12-slide Markdown deck is at `submission\review3-slide-deck.md`. GUI screenshots remain pending; exact manual capture steps are in `submission\evidence\README.md`.

Cassandra was not added during this pass because the proposal requirement was only just reconciled and no safe existing runtime was available: there is no Cassandra/cqlsh command, no Cassandra implementation directory, and Docker’s daemon is unavailable. The proposal also names Hive historical rollups, MLlib conjunction ranking, altitude-shell screening, and historical close-approach validation; these remain explicitly missing/unverified where no genuine evidence exists. HDFS/MapReduce/Hive files remain preserved, and no large D: Spark job was rerun. The project is not claimed 100% compliant.

The read-only full joined-dataset validation scanned `D:\Projects\space-debris-collision-risk\data\raw\tle_2023_2024_satcat_joined_clean.csv` (6,046,742,709 bytes) in 203.910 seconds: 29,136,654 data rows, 0 malformed rows, 0 invalid numeric values, 0 duplicate `(norad_id, epoch)` keys, and missing values only in `DECAY_DATE` (23,996,292), `LAUNCH_DATE` (102,729), and `intl_designator` (75,684). It found 31,937 unique NORAD IDs. Compared with the cleaned Parquet artifact: 31,516 IDs in common, 421 joined-only, and 36,613 Parquet-only. These artifacts are not row-equivalent.

The bounded Scala benchmark varied fixture partitions 1/2/4 and repeated each after compilation. Repeat wrapper times were 6.478/6.290/6.512 seconds, with identical six-record outputs and altitude sum 3245.0 km. This tiny local fixture benchmark includes JVM/Spark startup and does not establish distributed speedup.

Final smoke/regression evidence: `submission\evidence\pyspark-wsl-smoke-final.log` again ends with `smoke_status=PASS`, real worker paths, two partitions, and `spark_stopped=true`; `submission\evidence\python-tests-final.log` records 14 passing tests. Spark stderr warnings caused the PowerShell wrapper’s nonzero status but did not indicate application failure.

## Strict Review 3 final-submission audit — 2026-10-15

The controlling document was audited as `E:\Project Review3 Instructions.docx`; proposal-only Hive, Cassandra, HDFS/MapReduce, historical conjunction validation, and collision-risk MLlib items were not treated as Review 3 requirements. The detailed PASS/PARTIAL/UNVERIFIED matrix is `reports\review3-final-submission-audit.md`.

The external submission now contains `submission\project-report.md` with the required report sections and `submission\review3-slide-deck.md` with exactly 12 numbered slides in the required flow. The deck and report use only observed results and explicitly identify the PySpark target as SATCAT `OBJECT_TYPE`, not collision risk. Four actual EDA charts are linked from `reports\eda\`.

A bounded Scala run against 100 rows sampled from the real cleaned SATCAT Parquet artifact is preserved in `submission\evidence\scala-rdd-real-satcat-sample-20261015.log`. It observed 66 altitude-valid records, two partitions, DEB/PAY/R/B counts of 23/31/12, total filtered altitude 36,173.5 km, actual lineage, DAG explanation, and cached partitions. This closes the strict audit’s evidence gap without reading or rewriting the 6 GB D: dataset.

Remaining final-submission actions are administrative or format-related: fill team/register/department/institution metadata and render the Markdown report to the instructor-required format to verify the recommended 15–20 page length. No unsupported results should be added. The strict audit does not claim collision-risk modelling or full proposal compliance.

## Final Review 3 submission preparation — 2026-10-16

Reliable metadata from the root README was added to the report and deck: Kireeti (`CB.SC.U4CSE23057`), course `23CSE352 - Big Data Analytics`, and institution `Amrita Vishwa Vidyapeetham`. Department, any additional team members/register numbers, and faculty guide remain clearly marked `[TO SUPPLY]`; no personal or institutional details were guessed.

The report was rendered with the already-installed Microsoft Edge headless browser. Final artifacts are `submission\project-report.html` and `submission\project-report.pdf`. The PDF is 230,717 bytes and contains 8 pages. Structural validation found 8 page objects, 4 embedded image objects, no empty content arrays, and all four EDA image sources present. A browser preview of the cover and first page showed readable headings, metadata, tables, and no visible clipping or blank-page defect. The recommended 15–20 pages is not met; the report was not padded with unsupported content.

The presentation remains `submission\review3-slide-deck.md` with exactly 12 numbered slide headings. It is explicitly a Markdown deck and is not claimed to be a rendered PowerPoint or screenshot set. The strict audit and evidence index now record the PDF filename, page count, slide count, renderer, validation checks, and remaining manual metadata.

Final submission regression rerun: Python unittest `30/30` passed; Scala Maven `2/2` passed with `BUILD SUCCESS`; and the frontend Vite production build passed. Logs are `reports\python-tests-final-submission-20261016.log`, `reports\scala-maven-final-submission-20261016.log`, and `reports\frontend-build-final-submission-20261016.log`.

## Derived 100k leakage-controlled evaluation — 2026-10-16

The original D: joined dataset was scanned read-only with deterministic reservoir sampling. The sampler saw 29,136,654 valid rows, rejected 0, and wrote exactly 100,000 derived rows under C: at `data\joined_object_type_100k.csv`; the original dataset remains unchanged. The sample contains 26,261 unique NORAD IDs.

The supplemental PySpark job uses `OBJECT_TYPE` as its target, normalizes `UNKNOWN` to `UNK`, performs training-only imputation/scaling/label indexing, splits by NORAD-ID hash into 70,315 train / 19,660 validation / 10,025 test rows, tunes on validation macro-F1, and uses class weighting. Final test results: accuracy `0.517706`, macro-F1 `0.589657`, weighted precision `0.707602`, weighted recall `0.517706`. The majority baseline is accuracy `0.612369`, macro-F1 `0.189897`.

This lower raw accuracy is intentional and more defensible than optimizing for a headline number: the object-identity split prevents repeated observations from leaking across partitions, while class weighting improves minority balance. The 100k result is not directly comparable to the earlier 66.39% random-row split. It is not collision-risk prediction. Full methodology and evidence are in `reports\joined-100k-model-evaluation-20261016.md`.

## Modern dashboard update — 2026-10-16

The dashboard was redesigned under `frontend\src\main.tsx` and `frontend\src\style.css` with a modern responsive layout, plain-language labels, category bars, four real charts, searchable 100k catalog records, pagination, and a separate close-approach review panel. The visible interface does not expose implementation terms such as API, database, Spark, or model-training details. The 100k data is served by new project-local `/api/catalog-100k/summary` and `/api/catalog-100k/objects` routes.

Validation: frontend production build passed; Python suite passed 30/30; the new summary endpoint returned HTTP 200 with 100,000 rows; the object endpoint returned HTTP 200 with real catalog records. Close approaches remain labeled as review items, not confirmed collisions.

The trained model was also applied to the complete 100,000-row derived sample. Predictions are stored under `data\pyspark_ml_joined_100k\predictions_csv\` and the dashboard now shows each record’s known category beside its suggested category. Timestamp normalization was validated so all five sampled API rows returned predictions. These suggested categories are object-type classifications only; no collision-risk prediction is presented.
