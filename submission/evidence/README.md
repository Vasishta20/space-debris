# Genuine evidence index for submission

The files in this directory are copied from actual project outputs; no screenshots or metric values were fabricated.

## Available evidence

- `eda-*.png`: actual Matplotlib plots generated from the SATCAT artifact.
- `screening.json` and `screening_prioritized.json`: actual bounded SGP4 candidate and separate heuristic prioritization output.
- `pyspark-wsl-smoke.log`: actual WSL2 distributed worker action.
- `pyspark-ml-validation.log` and `pyspark-validation-metrics.json`: actual PySpark ML validation, class metrics, majority baseline, and reload equivalence.
- `scala-rdd-output.log` and `fault-tolerance.log`: actual RDD and retry/recomputation outputs.
- `python-tests.log`: actual Python unittest summary.

## Manual GUI capture steps

GUI screenshots were not captured automatically because no screenshot-capable browser/desktop connector was available. To complete the visual submission evidence manually:

1. Start the backend with `C:\space-debris-collision-risk-output\project\scripts\start-backend.ps1`.
2. Start the frontend with `C:\space-debris-collision-risk-output\project\scripts\start-frontend.ps1`.
3. Open the reported local frontend URL and capture the dashboard, object search, candidate table, and model metrics panel.
4. Open `http://127.0.0.1:8000/docs` and capture the FastAPI documentation and one successful response.
5. Stop processes started for capture and record the filenames in `reports/evidence-index.md`.

Those pending screenshots must not be represented as completed evidence until genuinely captured.
