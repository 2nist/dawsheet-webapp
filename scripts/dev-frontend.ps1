param(
    [int]$Port = 3000
)

Write-Host "Starting frontend development helper (port $Port)"

$webDir = Join-Path $PSScriptRoot "..\web"
Set-Location $webDir

Write-Host "Installing dependencies (if needed) and starting Next dev server"
if (-not (Test-Path "node_modules")) {
    npm install
}

npm run dev --silent -- -p $Port
