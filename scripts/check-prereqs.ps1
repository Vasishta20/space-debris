$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Py = Join-Path $Root '.venv\Scripts\python.exe'
if (!(Test-Path $Py)) { throw "Missing isolated Python: $Py" }
if (!(Get-Command node -ErrorAction SilentlyContinue)) { throw 'Node.js is required for the frontend.' }
if (!(Test-Path (Join-Path $Root 'frontend\node_modules'))) { throw 'Run npm install in frontend first.' }
& $Py -c "import fastapi,sgp4; print('Python dependencies: OK')"
node --version
Write-Output "Prerequisites: OK"
