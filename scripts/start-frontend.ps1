$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
if (!(Test-Path (Join-Path $Root 'frontend\node_modules'))) { throw 'Run npm install in frontend first.' }
Push-Location (Join-Path $Root 'frontend')
try { npm run dev -- --host 127.0.0.1 --port 5173 } finally { Pop-Location }
