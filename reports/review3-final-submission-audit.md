# Review 3 Final Submission Audit

**Controlling document:** `E:\Project Review3 Instructions.docx` (Project Review 3 — Apache Spark, 15 marks)  
**Audit date:** 2026-10-15  
**Workspace:** `C:\space-debris-collision-risk-output\project`

This audit uses the attached Review 3 instructions and rubric only. Hive, Cassandra, HDFS/MapReduce proposal items, and other technologies not required by that rubric are excluded from the checklist. The PySpark model is explicitly an SATCAT `OBJECT_TYPE` classifier, not a collision-risk model.

## Requirement checklist

| Review 3 requirement | Status | Evidence | Exact remaining action |
|---|---|---|---|
| Real-world dataset selected and described | PASS | `submission/project-report.md` §4; `data/satcat_clean.json`; `reports/eda/eda.json` | Add team metadata if required by the institution. |
| Problem/application is meaningful | PASS | `submission/project-report.md` §§1–3; `submission/review3-slide-deck.md` slides 1–2 | None for rubric evidence. |
| Scala/Spark RDD created from dataset | PASS (bounded) | `phase-2b/spark-rdd/src/main/scala/org/course/spacedebris/rdd/RddDemo.scala`; `submission/evidence/scala-rdd-real-satcat-sample-20261015.log` | None. The run is intentionally a 100-row sample derived from real Parquet, not the 6 GB input. |
| At least three meaningful transformations | PASS | Source and real-data log: `repartition`, `map`, `flatMap`, `filter`, `reduceByKey`, `distinct` | None. |
| At least two actions | PASS | Real-data log shows `count`, `collect`, `take`, and `reduce` outputs | None. |
| Key-value RDD operations | PASS | `reduceByKey`/sorted category output in source and log | None. |
| Partition count | PASS | Real-data log: requested/before/after = 2 | None. |
| RDD lineage and DAG explanation | PASS | `toDebugString` and `dag=` lines in `submission/evidence/scala-rdd-real-satcat-sample-20261015.log`; report §6 | None. |
| Cache/persist demonstrated | PASS | `valid_before_cache`, `valid_after_cache`, and cached partitions in real-data log | None. |
| Fault tolerance explained | PASS with scope limitation | `submission/evidence/fault-tolerance.log`; report §6; `submission/review3-slide-deck.md` slide 6 | Evidence is bounded task retry/recomputation only; do not describe it as machine recovery. |
| PySpark feature preparation | PASS | `scripts/pyspark_ml_object_type.py`; `data/pyspark_ml_validation_20261015/metrics.json`; report §7 | None for object-type task. |
| Train/test split | PASS | Metrics JSON: seed 42, 51,027 train and 17,102 test rows | None. |
| PySpark ML model | PASS | Metrics JSON and WSL execution log; report §7 | None. The target is object type, not collision risk. |
| Evaluation with appropriate metrics | PASS | Accuracy 0.663899, macro-F1 0.627583, class metrics and majority baseline in metrics JSON | None. |
| At least three meaningful charts | PASS | `reports/eda/apogee_hist.png`, `perigee_hist.png`, `inclination_hist.png`, `object_type_counts.png`; `reports/eda/eda.json` | None. |
| Presentation is complete and ≤12 slides | PASS | `submission/review3-slide-deck.md`: exactly 12 numbered slide headings, required flow, actual metrics/charts | Add team/register numbers and institution details before submission. |
| Project report follows required structure | PARTIAL | `submission/project-report.md` contains title, introduction, problem, objectives, dataset, methodology, Scala/Spark, PySpark ML, visualization, results, conclusion, references, evidence | Add team/department/institution fields and render/check the final document against the instructor's recommended 15–20 page format if a PDF/DOCX is required. |
| Report recommended length | UNVERIFIED | Markdown report is complete but page count depends on rendering | Render to the required submission format and verify 15–20 pages; do not pad with unsupported claims. |
| Reported metrics/results backed by execution evidence | PASS | EDA JSON/PNGs; PySpark metrics JSON and WSL log; RDD logs; screening JSON; evidence index | None; preserve the referenced logs with submission. |

## Evidence-backed results

- SATCAT EDA: 68,129 rows, zero reported missing values for the checked numeric fields, and four generated charts. Metadata is in `reports/eda/eda.json`.
- Real-data RDD sample: 100 source-derived rows, 66 altitude-valid rows, two partitions, category counts DEB 23 / PAY 31 / R/B 12, and total filtered altitude 36,173.5 km. The complete application output is in `submission/evidence/scala-rdd-real-satcat-sample-20261015.log`.
- PySpark: Spark/PySpark 3.5.1, Python 3.12.3, Java 11.0.32, 51,027/17,102 split, accuracy 0.663899, macro-F1 0.627583. These metrics are for `OBJECT_TYPE` classification.
- Fault tolerance: the disposable fixture records a deterministic task retry/recomputation and recovered sum 36. It does not validate executor loss, machine recovery, or production resilience.
- Screening: the bounded SGP4 result is a candidate close approach, not a confirmed collision or calibrated probability.

## Exact validation commands

The final bounded regression commands and outputs are recorded in:

- `reports/python-tests-review3-final-audit-20261015.log`
- `reports/scala-maven-review3-final-audit-20261015.log`
- `reports/pyspark-wsl-smoke-review3-final-audit-20261015.log`
- `reports/frontend-build-review3-final-audit-20261015.log`

The commands use the project-local Python environment, the isolated JDK 17 for Scala Maven, the existing WSL2 PySpark environment, and the existing frontend dependencies. No dependency files, global environment settings, D: files, Hive, or Cassandra were changed.

## Final status

The strict Review 3 implementation evidence is substantially complete: RDD concepts, PySpark object-type ML, evaluation, and visualizations are PASS. The remaining submission actions are administrative/document-format completion (team/register/institution metadata and rendered report length). Collision-risk ML, historical conjunction validation, and proposal-only Hive/Cassandra evidence are not Review 3 pass criteria and remain outside this audit.

## Submission preparation validation — 2026-10-16

- Known identity details were filled from the repository README: Kireeti (`CB.SC.U4CSE23057`), course `23CSE352 - Big Data Analytics`, and institution `Amrita Vishwa Vidyapeetham`.
- Department, additional team members/register numbers, and faculty guide remain explicit `[TO SUPPLY]` placeholders because no reliable values were found in project files.
- Final report source: `submission/project-report.md`.
- Rendered report: `submission/project-report.pdf` (230,717 bytes; 8 pages).
- Render source: `submission/project-report.html`; renderer: existing Microsoft Edge headless, with no package installation.
- PDF structural checks: valid `%PDF-1.4` header, 8 page objects, 4 embedded image objects, zero empty content arrays. All four chart source files exist and are referenced by the HTML.
- Visual check: the rendered cover and first report page were inspected; headings, metadata, code styling, and layout are readable with no visible clipping or blank-page defect. Full report content remains source-backed. The recommended 15–20 pages is not met; the report was not padded with unsupported material.
- Presentation source: `submission/review3-slide-deck.md`; exactly 12 numbered slide headings. It is a Markdown deck, not a claimed PowerPoint or screenshot set.
