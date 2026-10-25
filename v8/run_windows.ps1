$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
$python="$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
if (-not (Test-Path $python)) { throw "Python 3.13 not found at $python" }
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { throw "Install Node.js LTS first." }
if (-not (Test-Path node_modules)) {
  Write-Host "Installing Remotion dependencies ..."
  npm.cmd install
  if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
}
Write-Host "VOICEVOX and optional Pixabay asset preparation ..."
& $python prepare.py
if ($LASTEXITCODE -ne 0) { throw "Preparation failed: start VOICEVOX and check any errors above" }
New-Item -ItemType Directory -Path out -Force | Out-Null
Write-Host "Rendering Magnum short: 45 seconds, 9:16, 30fps ..."
npx.cmd remotion render src/index.tsx Magnum45 out/magnum45.mp4 --codec=h264 --concurrency=2 --props=render-props.json
if ($LASTEXITCODE -ne 0) { throw "Remotion render failed" }
$video=Join-Path $PSScriptRoot "out\magnum45.mp4"
Write-Host "Done: $video" -ForegroundColor Green
Start-Process $video
