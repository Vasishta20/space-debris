# Space Debris Collision Risk Analytics — Review 3 presentation

**Course:** 23CSE352 – Big Data Analytics  
**Team member:** Kireeti - CB.SC.U4CSE23057  
**Additional team members/register numbers:** [TO SUPPLY, if applicable]  
**Department:** [TO SUPPLY: department name]  
**Institution:** Amrita Vishwa Vidyapeetham  
**Review:** Project Review 3 — Apache Spark

## 1. Title and objective

This project applies Spark-based processing to a real SATCAT orbital catalog and demonstrates bounded orbital screening. Screening candidates are not confirmed collisions, collision probabilities, or risk labels.

## 2. Problem statement

Orbital catalogs contain heterogeneous objects and numeric orbital attributes. The goal is to process real records, summarize them, demonstrate Spark RDD concepts, evaluate a reproducible ML task, and communicate limitations honestly.

## 3. Dataset

The cleaned SATCAT catalog contains 68,129 real records. Important attributes include object ID, NORAD ID, object type, owner, period, inclination, apogee, perigee, radar cross-section, orbit center, and orbit type. The source is recorded in `data/satcat_clean.json`; the original D: input was preserved.

Object types: DEB 34,568; PAY 26,830; R/B 6,571; UNK 160. The target used for ML is `OBJECT_TYPE`, not collision risk.

## 4. Workflow

```text
SATCAT -> validation/Parquet -> Scala Spark RDD -> PySpark features/split/model
       -> held-out metrics -> EDA charts -> bounded SGP4 screening and API
```

The 6 GB joined dataset was not copied or used for a full-catalog job.

## 5. Scala + Spark RDD

The final RDD job reads the single canonical Review 3 catalog with `textFile`, then uses `repartition`, `map`, `flatMap`, and `filter`. It uses `reduceByKey` and `sortByKey` for category aggregation, plus `distinct`, `sortBy`, and `take` for aliases.

Actions include `count`, `collect`, `take`, and `reduce`. The final catalog run processed the canonical CSV; 91,372 valid records passed the altitude filter, with DEB 28,988, PAY 55,016, R/B 6,331, and UNK 1,037.

## 6. Spark concepts

The final run used four partitions and printed actual `toDebugString` lineage containing the source HadoopRDD, repartition, map, flatMap, filter, and cached partitions. The printed DAG explains the persisted branch and aggregation branches. `persist()` was demonstrated by repeated actions and cached partition reporting.

A disposable fixture showed one task retry and recomputation: attempt 0 failed, attempt 1 succeeded, and the recovered sum was 36. This is task retry evidence, not machine or executor recovery.

## 7. Data processing results

The bounded ingestion loaded 68,129 records with zero rejected rows. The SGP4 demonstration used 60 real Starlink TLEs, seven UTC epochs, a ten-minute step, TEME coordinates, and a 50 km threshold. It produced one screening candidate at 19.837 km separation and 0.216 km/s relative velocity.

## 8. PySpark ML

The verified WSL2 run used Spark/PySpark 3.5.1, Python 3.12.3, and Java 11.0.32. Features were PERIOD, INCLINATION, APOGEE, PERIGEE, and RCS. Training-fitted median imputation, vector assembly, label indexing, a seed-42 75/25 split, and logistic regression were used.

## 9. Model evaluation

Held-out accuracy was 0.663899 and macro-F1 was 0.627583. The majority baseline was 0.511753 accuracy and 0.169258 macro-F1. Class F1 values were DEB 0.754435, PAY 0.610807, R/B 0.038328, and UNK 0.000000.

This is SATCAT object-type classification. It is not a collision-risk model, conjunction classifier, or probability estimate.

## 10. Visualization

The following four charts are genuine outputs from the 68,129-row EDA run:

![Apogee distribution](../reports/eda/apogee_hist.png)

![Perigee distribution](../reports/eda/perigee_hist.png)

![Inclination distribution](../reports/eda/inclination_hist.png)

![Object type counts](../reports/eda/object_type_counts.png)

## 11. Results and discussion

The RDD, PySpark preprocessing/model/evaluation, and visualization requirements are supported by execution evidence. The object-type model improves on the majority baseline but has weak minority-class performance. The bounded SGP4 result is useful for screening demonstration only; independent historical conjunction labels and uncertainty-aware collision-risk data are not available.

## 12. Conclusion and references

Review 3 evidence is complete for the demonstrated Spark workflow, object-type ML task, and charts, subject to the audit limitations. Team/register details and any institution-specific report formatting must be added before submission.

References and reproducibility paths: `submission/project-report.md`, `reports/review3-final-submission-audit.md`, `submission/evidence/`, `data/eda.json`, and the Apache Spark documentation referenced by the source files.
