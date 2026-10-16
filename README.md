# Space Debris Collision Risk Analytics

This repository contains the complete Spark/Scala, PySpark, analytics, FastAPI,
React, database, report, and presentation implementation. The original D:
repository and its large joined dataset are not modified or copied.

## Structure

- `phase-2b/spark-rdd/` — Scala 2.12 and Spark 3.5.1 RDD analysis.
- `scripts/` — ingestion, EDA, PySpark ML, orbital screening, and validation.
- `app/` — FastAPI backend, SQLite/PostgreSQL access, orbit screening, and API routes.
- `frontend/` — React + TypeScript dashboard using live API responses.
- `data/` — the canonical catalog, model evidence, charts, and bounded screening outputs.
- `submission/` — project report, PDF, presentation, and evidence logs.

## Run

```powershell
$root = 'C:\space-debris-collision-risk-output\project'
& "$root\.venv\Scripts\python.exe" "$root\scripts\run_pipeline.py"
& "$root\.venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir $root --host 127.0.0.1 --port 8000
```

The bounded pipeline reads `data/raw/satcat_clean.csv` from the original repository (about 6.9 MB), not the 6 GB joined input. TLE screening downloads one bounded CelesTrak group into this output directory and records its source URL.

The classifier predicts SATCAT `OBJECT_TYPE`; it is not a collision probability model and must not be presented as one. Close-approach screening is a small, deterministic demonstration over downloaded TLEs and does not replace high-fidelity conjunction assessment.

## Scala RDD execution

```powershell
$base = 'C:\space-debris-collision-risk-output\project'
$module = "$base\phase-2b\spark-rdd"
$catalog = "$base\data\review3_catalog.csv"
$env:JAVA_HOME = 'C:\space-debris-collision-risk-output\tools\jdk-17.0.20.1+1'
$env:JAVA_TOOL_OPTIONS = '--add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED --add-opens=java.base/java.lang.invoke=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED'
mvn -f "$module\pom.xml" test
mvn -f "$module\pom.xml" compile exec:java "-Dexec.args=$catalog 4" "-Dexec.cleanupDaemonThreads=false"
```

## Frontend

```powershell
Push-Location "$root\frontend"
npm install
npm run build
npm run dev -- --host 127.0.0.1 --port 5173
Pop-Location
```

Start the API separately with `scripts\start-backend.ps1`. The React client calls the live API and displays explicit object-type and candidate-screening limitations.
