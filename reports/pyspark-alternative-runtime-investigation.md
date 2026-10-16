# PySpark alternative-runtime investigation

Date: 2026-10-14. Scope: read-only runtime inspection plus bounded existing-runtime checks. No packages, WSL configuration, Docker services, or system settings were changed.

## Available runtimes

| Runtime | Observed result | Decision |
|---|---|---|
| Windows Python | Python 3.12.0 at the existing global installation and project-local `phase-2b\.venv` | Existing Windows runtime remains blocked by the worker EOF failure. |
| Python 3.11 | No installed Python 3.11 executable was found under the inspected local Python locations. | Not available without installation. |
| Windows Java | Isolated Temurin 17.0.20.1 | Gateway starts, but Python worker exits unexpectedly. |
| WSL2 Ubuntu | Ubuntu is installed, stopped initially, and WSL version 2. It provides Linux kernel `6.6.87.2-microsoft-standard-WSL2`, Python 3.12.3, `/usr/bin/java` linked to Java 11, and the C: project mount. `pip` and `spark-submit` are absent. | Not usable without installing Python packages/Spark or changing the environment. No installation was attempted. |
| Docker | Docker CLI 29.1.3 is on PATH. `docker version` could not connect to the Docker Desktop Linux engine named pipe. | Daemon unavailable; Docker was not started. |

## Existing Windows evidence

The prior diagnostic recorded:

- Driver: `C:\space-debris-collision-risk-output\phase-2b\.venv\Scripts\python.exe`, Python 3.12.0.
- Java: isolated Temurin 17.0.20.1.
- Spark/PySpark: 3.5.1.
- `SPARK_HOME`: extracted runtime `deps` directory.
- Effective Spark launch command included explicit `spark.pyspark.python`, `spark.executorEnv.PYSPARK_PYTHON`, and venv `PYTHONPATH` settings.
- A spawned process nevertheless resolved to `C:\Users\dsvas\AppData\Local\Programs\Python\Python312\python.exe` and the minimal action failed with `SparkException: Python worker exited unexpectedly (crashed)` caused by `java.io.EOFException`.

The direct Python launch, `spark-submit.cmd`, PATH/interpreter propagation, and unsetting `PYSPARK_DRIVER_PYTHON` were already tested. Repeating those variants is not justified by new evidence.

## Superseded conclusion

The original read-only conclusion above was valid before the separately approved WSL2 setup. It is superseded by `reports/pyspark-wsl-ml.md`: Ubuntu package support was installed inside the existing WSL distribution, a real PySpark worker action passed, and the bounded object-type PySpark ML run completed. The native Windows EOF failure remains unresolved and is retained as a runtime-specific limitation.

Current evidence: `reports\pyspark-wsl-ml.md`, `reports\pyspark-wsl-smoke.log`, `reports\pyspark-ml-wsl.log`, and `data\pyspark_ml_object_type\metrics.json`.
