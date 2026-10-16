# Joined 100k Object-Type Model Evaluation

Date: 2026-10-16  
Scope: supplemental, leakage-controlled SATCAT `OBJECT_TYPE` classification. This is not a collision-risk model.

## Derived data

`scripts/sample_joined_100k.py` performed one-pass deterministic reservoir sampling from the original D: joined CSV. The source was read sequentially and not modified. It scanned 29,136,654 valid rows, rejected 0 rows, and wrote exactly 100,000 derived rows to `data/joined_object_type_100k.csv` on C:. The sample contains 26,261 unique NORAD IDs. Sampling seed: 20261016.

Source metadata and class counts are in `data/joined_object_type_100k_metadata.json`.

## Method

The PySpark job is `scripts/pyspark_ml_joined_100k.py` and ran in the existing WSL2 Spark/PySpark 3.5.1 environment. Numeric TLE/orbital features were imputed and standardized using training data only. `UNKNOWN` and `UNK` were normalized to the documented `UNK` class. The split is deterministic by NORAD-ID hash: 70,315 train rows, 19,660 validation rows, and 10,025 test rows. Hyperparameters were selected using validation macro-F1; the test set was used once for final metrics.

The selected weighted logistic-regression configuration was `regParam=0.0`, `elasticNetParam=0.0`. Class weights were calculated from the training partition. Saved artifacts are under `data/pyspark_ml_joined_100k/`.

## Observed test results

| Metric | Result |
|---|---:|
| Accuracy | 0.517706 |
| Macro-F1 | 0.589657 |
| Weighted precision | 0.707602 |
| Weighted recall | 0.517706 |
| Majority baseline accuracy | 0.612369 |
| Majority baseline macro-F1 | 0.189897 |

Class-level F1: PAY 0.645663, DEB 0.556430, R/B 0.373593, and UNK 0.047601.

## Interpretation and limitation

The class-weighted model improves balanced performance substantially over the majority baseline, but it does not improve raw accuracy over that baseline. This is not a failure to hide: class weighting deliberately trades some majority-class accuracy for minority-class recall. The prior 66.39% result used the 68,129-row cleaned catalog with a random row split; it is not directly comparable because this experiment uses repeated joined observations and an object-identity split. No metric was selected by inspecting the test set.

The target remains SATCAT object type. These results must not be described as collision-risk accuracy, probability, or conjunction prediction.

## Commands and evidence

```powershell
$root = 'C:\space-debris-collision-risk-output\project'
$py = "$root\.venv\Scripts\python.exe"
& $py "$root\scripts\sample_joined_100k.py" `
  --source 'D:\Projects\space-debris-collision-risk\data\raw\tle_2023_2024_satcat_joined_clean.csv' `
  --output "$root\data\joined_object_type_100k.csv" `
  --metadata "$root\data\joined_object_type_100k_metadata.json" `
  --size 100000 --seed 20261016

wsl.exe -d Ubuntu -- bash -lc "timeout 600s /home/dsvasi/pyspark-wsl-venv/bin/python /mnt/c/space-debris-collision-risk-output/project/scripts/pyspark_ml_joined_100k.py --input /mnt/c/space-debris-collision-risk-output/project/data/joined_object_type_100k.csv --output /mnt/c/space-debris-collision-risk-output/project/data/pyspark_ml_joined_100k"
```

The first ML log records a corrected setup error (`label` was referenced before grouping by `OBJECT_TYPE`); the rerun log ends with `ml_status=PASS`: `reports/pyspark-ml-joined-100k-20261016-rerun.log`.
