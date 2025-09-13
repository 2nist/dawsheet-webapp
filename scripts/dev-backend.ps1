param(
    [int]$Port = 8000
)

Write-Host "Starting backend development helper (port $Port)"

$backendDir = Join-Path $PSScriptRoot "..\backend"
Set-Location $backendDir

if (-not (Test-Path ".\venv")) {
    Write-Host "Virtual environment not found. Creating .\venv..."
    python -m venv .\venv
    & .\venv\Scripts\pip.exe install -r requirements.txt
} else {
    Write-Host "Using existing virtual environment .\venv"
}

Write-Host "Activating virtual environment and starting uvicorn..."
Write-Host "If you want to stop Docker Desktop to avoid port conflicts, run: wsl --shutdown" -ForegroundColor Yellow

& .\venv\Scripts\Activate.ps1

# Run uvicorn in the current shell (blocking). Use Ctrl+C to stop.
python -m uvicorn server:app --host 0.0.0.0 --port $Port
