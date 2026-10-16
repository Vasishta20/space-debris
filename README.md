# Space Debris Collision Risk Analytics — external C: backend

This is an isolated implementation workspace. The original repository and its 6 GB joined dataset are not modified or copied.

## Run

```powershell
$root = 'C:\space-debris-collision-risk-output\project'
& "$root\.venv\Scripts\python.exe" "$root\scripts\run_pipeline.py"
& "$root\.venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir $root --host 127.0.0.1 --port 8000
```

The bounded pipeline reads `data/raw/satcat_clean.csv` from the original repository (about 6.9 MB), not the 6 GB joined input. TLE screening downloads one bounded CelesTrak group into this output directory and records its source URL.

The classifier predicts SATCAT `OBJECT_TYPE`; it is not a collision probability model and must not be presented as one. Close-approach screening is a small, deterministic demonstration over downloaded TLEs and does not replace high-fidelity conjunction assessment.

## Frontend

```powershell
Push-Location "$root\frontend"
npm install
npm run build
npm run dev -- --host 127.0.0.1 --port 5173
Pop-Location
```

Start the API separately with `scripts\start-backend.ps1`. The React client calls the live API and displays explicit object-type and candidate-screening limitations.
