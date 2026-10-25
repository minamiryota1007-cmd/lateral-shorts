$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$python = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
if (-not (Test-Path $python)) { throw "Python 3.13 missing: $python" }
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { throw "Node.js LTS is required." }
if (-not (Test-Path node_modules)) {
  Write-Host "[1/4] Installing Remotion ..." -ForegroundColor Cyan
  npm.cmd install
  if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
}
Write-Host "[2/4] Recalculating toy-model physics and exporting JSON ..." -ForegroundColor Cyan
& $python physics.py
if ($LASTEXITCODE -ne 0) { throw "Physics step failed" }
Write-Host "[3/4] Narration + background assets ..." -ForegroundColor Cyan
& $python prepare.py
if ($LASTEXITCODE -ne 0) { throw "Preparation failed; check VOICEVOX and speech length" }
New-Item -ItemType Directory -Force -Path out | Out-Null
Write-Host "[4/4] Rendering 45s 1080x1920 / 30fps ..." -ForegroundColor Cyan
npx.cmd remotion render src/index.tsx MagnumV9 out/magnum_v9.mp4 --codec=h264 --concurrency=2 --props=render-props.json
if ($LASTEXITCODE -ne 0) { throw "Remotion render failed" }
$result=Join-Path $PSScriptRoot "out\magnum_v9.mp4"
Write-Host "SUCCESS: $result" -ForegroundColor Green
Start-Process $result
