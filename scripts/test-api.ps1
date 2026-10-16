$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Py = Join-Path $Root '.venv\Scripts\python.exe'
& $Py -m unittest discover -s (Join-Path $Root 'tests') -v
& $Py -c "import httpx; r=httpx.get('http://127.0.0.1:8000/health',timeout=5); r.raise_for_status(); print(r.json())"
