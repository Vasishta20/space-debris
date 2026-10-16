# Next-phase command checklist

```powershell
$root = 'C:\space-debris-collision-risk-output\project'
$py = "$root\.venv\Scripts\python.exe"

# Re-run bounded analytics and evidence generation
& $py "$root\scripts\run_pipeline.py"

# Verify persistence and API without starting a long-lived service
& $py -m unittest discover -s "$root\tests" -v
& $py -c "from fastapi.testclient import TestClient; from app.main import app; c=TestClient(app); print(c.get('/health').json()); print(c.get('/api/summary').json())"

# Start the local API only when needed
& $py -m uvicorn app.main:app --app-dir $root --host 127.0.0.1 --port 8000
```

Do not run the pipeline against `tle_2023_2024_satcat_joined_clean.csv`; it is preserved input and D: is full. Do not install system-wide dependencies or start Docker/PostgreSQL without a new explicit approval.
