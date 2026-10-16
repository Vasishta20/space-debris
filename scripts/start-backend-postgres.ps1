$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$env:DATABASE_URL = 'postgresql://postgres@127.0.0.1:55432/postgres'
& (Join-Path $Root '.venv\Scripts\python.exe') -m uvicorn app.main:app --app-dir $Root --host 127.0.0.1 --port 8000
