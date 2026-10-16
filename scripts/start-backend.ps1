$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
& (Join-Path $PSScriptRoot 'check-prereqs.ps1')
& (Join-Path $Root '.venv\Scripts\python.exe') -m uvicorn app.main:app --app-dir $Root --host 127.0.0.1 --port 8000
