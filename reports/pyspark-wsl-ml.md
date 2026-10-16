# WSL2 PySpark and ML verification

Date: 2026-10-15. This is an isolated Ubuntu runtime; the original Hadoop repository and D: data were not used or modified.

## Environment

- WSL2 Ubuntu 24.04.3 LTS, x86_64; kernel `6.6.87.2-microsoft-standard-WSL2`.
- Python 3.12.3 at `/usr/bin/python3`.
- Java 11.0.32 at `/usr/bin/java`.
- PySpark/Spark 3.5.1 and py4j 0.10.9.7 in `/home/dsvasi/pyspark-wsl-venv`.
- The venv is on Ubuntu ext4 because pip stalled on the mounted C: filesystem; project scripts, logs, metrics, and model artifacts remain under this C: project.
- Project preflight: C: had approximately 131.69 GB free; WSL `/` had 943 GB free. No system-wide Python, Java, PATH, or Windows configuration was changed.

## Worker smoke test

Command:

```powershell
wsl.exe -d Ubuntu -- timeout 90s /home/dsvasi/pyspark-wsl-venv/bin/python /mnt/c/space-debris-collision-risk-output/project/scripts/pyspark_wsl_smoke.py
```

Observed result in `reports/pyspark-wsl-smoke.log`: `local[2]`, two partitions, result `[2, 4, 6, 8, 10, 12, 14, 16]`, and `smoke_status=PASS`. The actual worker identity was `/usr/bin/python3`, Python 3.12.3, on both partitions. Spark stopped cleanly. The PowerShell pipeline surfaced Spark warnings on stderr and returned 1 despite the application-level PASS; the log is the source of truth.

## ML run

Command:

```powershell
wsl.exe -d Ubuntu -- timeout 180s /home/dsvasi/pyspark-wsl-venv/bin/python /mnt/c/space-debris-collision-risk-output/project/scripts/pyspark_ml_object_type.py --input /mnt/c/space-debris-collision-risk-output/project/data/satcat_clean.parquet --output /mnt/c/space-debris-collision-risk-output/project/data/pyspark_ml_object_type
```

The bounded Parquet input contains 68,129 rows and labels DEB, PAY, R/B, and UNK. The pipeline uses only `PERIOD`, `INCLINATION`, `APOGEE`, `PERIGEE`, and `RCS`; IDs and the target are excluded from features. It performs a seed-42 75/25 split, fits median imputation, vector assembly, and label indexing within the training pipeline, and evaluates a logistic-regression classifier on the held-out test set.

Observed metrics in `data/pyspark_ml_object_type/metrics.json`:

- train/test rows: 51,027 / 17,102
- accuracy: 0.6638989592
- macro-F1: 0.6275827871
- class support: DEB 8,752; PAY 6,658; R/B 1,653; UNK 39

The saved Spark model is under `data/pyspark_ml_object_type/model`. This is a genuine object-type classification model, not a collision-risk classifier or probability estimate.

## Compatibility notes and limitations

The approved WSL installation added Ubuntu `python3-pip` and `python3-venv`, then project-runtime packages PySpark 3.5.1, NumPy 1.26.4, and setuptools 69.5.1. NumPy was required by `pyspark.ml`; setuptools supplied the `distutils` compatibility import needed by this PySpark 3.5.1/Python 3.12 combination. Installation output is in `reports/wsl-pyspark-setup.log`, `reports/wsl-pyspark-install.log`, and the ML run is in `reports/pyspark-ml-wsl.log`.

Spark warnings about the hostname loopback mapping and native Hadoop library are non-fatal. No full joined dataset job, collision-risk label, or orbital ML model was run.
