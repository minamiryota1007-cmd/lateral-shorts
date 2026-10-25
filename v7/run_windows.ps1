$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "Lateral Shorts V7 - Remotion" -ForegroundColor Cyan

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "Node.js/npm is not installed. Install Node.js LTS first from https://nodejs.org/ and reopen PowerShell."
}
$python = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
if (-not (Test-Path $python)) {
    throw "Python 3.13 not found at $python"
}
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing Remotion packages (first run only)..."
    npm install
    if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
}
Write-Host "Preparing VOICEVOX narration..."
& $python "prepare_voice.py"
if ($LASTEXITCODE -ne 0) { throw "Voice preparation failed" }
New-Item -ItemType Directory -Force -Path "out" | Out-Null
Write-Host "Rendering 1080x1920 / 30fps..."
npx remotion render src/index.tsx LateralV7 out/lateral_v7.mp4 --props=render-props.json --codec=h264 --concurrency=2
if ($LASTEXITCODE -ne 0) { throw "Remotion render failed" }
Write-Host "Done: $PSScriptRoot\out\lateral_v7.mp4" -ForegroundColor Green
Start-Process (Join-Path $PSScriptRoot "out\lateral_v7.mp4")
