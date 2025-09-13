# Robust Server Manager for Dawsheet
# This script monitors and auto-restarts servers when they crash

param(
    [switch]$NoRestart,
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 3000,
    [int]$CheckInterval = 5
)

$ErrorActionPreference = "SilentlyContinue"

Write-Host "🔧 Dawsheet Robust Server Manager" -ForegroundColor Green
Write-Host "Backend Port: $BackendPort | Frontend Port: $FrontendPort" -ForegroundColor Cyan
Write-Host "Check Interval: $CheckInterval seconds" -ForegroundColor Cyan
Write-Host "Auto-restart: $(-not $NoRestart)" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop all servers`n" -ForegroundColor Yellow

# Global variables to track jobs
$global:BackendJob = $null
$global:FrontendJob = $null
$global:BackendPID = $null
$global:FrontendPID = $null

# Function to check if a port is in use
function Test-PortInUse {
    param([int]$Port)
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        return $connection -ne $null
    }
    catch {
        return $false
    }
}

# Function to test HTTP endpoint
function Test-Endpoint {
    param([string]$Url)
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

# Function to kill process by port
function Stop-ProcessByPort {
    param([int]$Port)
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if ($connection) {
            $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "🛑 Stopping process $($process.ProcessName) (PID: $($process.Id)) on port $Port" -ForegroundColor Red
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2
            }
        }
    }
    catch {
        Write-Host "⚠️ Could not stop process on port $Port" -ForegroundColor Yellow
    }
}

# Function to start backend
function Start-BackendServer {
    Write-Host "🐍 Starting Backend Server..." -ForegroundColor Cyan

    # Kill any existing backend process
    Stop-ProcessByPort $BackendPort

    # Start new backend job
    $global:BackendJob = Start-Job -ScriptBlock {
        param($Port)
        Set-Location "C:\Users\CraftAuto-Sales\dawsheet\webapp"
        python -m uvicorn minimal_server:app --host 0.0.0.0 --port $Port --log-level warning
    } -ArgumentList $BackendPort

    # Wait and verify
    Start-Sleep -Seconds 3
    if (Test-PortInUse $BackendPort) {
        Write-Host "✅ Backend started on http://localhost:$BackendPort" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ Backend failed to start" -ForegroundColor Red
        return $false
    }
}

# Function to start frontend
function Start-FrontendServer {
    Write-Host "⚛️ Starting Frontend Server..." -ForegroundColor Cyan

    # Kill any existing frontend process
    Stop-ProcessByPort $FrontendPort

    # Start new frontend job
    $global:FrontendJob = Start-Job -ScriptBlock {
        param($Port)
        Set-Location "C:\Users\CraftAuto-Sales\dawsheet\webapp\web"
        npx next dev -p $Port
    } -ArgumentList $FrontendPort

    # Wait and verify
    Start-Sleep -Seconds 8
    if (Test-PortInUse $FrontendPort) {
        Write-Host "✅ Frontend started on http://localhost:$FrontendPort" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ Frontend failed to start" -ForegroundColor Red
        return $false
    }
}

# Function to check server health
function Test-ServerHealth {
    $backendOk = Test-Endpoint "http://localhost:$BackendPort/api/health"
    $frontendOk = Test-PortInUse $FrontendPort

    $status = @{
        Backend = $backendOk
        Frontend = $frontendOk
        Timestamp = Get-Date -Format "HH:mm:ss"
    }

    return $status
}

# Cleanup function
function Stop-AllServers {
    Write-Host "`n🛑 Shutting down all servers..." -ForegroundColor Red

    Stop-ProcessByPort $BackendPort
    Stop-ProcessByPort $FrontendPort

    if ($global:BackendJob) {
        Stop-Job $global:BackendJob -ErrorAction SilentlyContinue
        Remove-Job $global:BackendJob -ErrorAction SilentlyContinue
    }

    if ($global:FrontendJob) {
        Stop-Job $global:FrontendJob -ErrorAction SilentlyContinue
        Remove-Job $global:FrontendJob -ErrorAction SilentlyContinue
    }

    Write-Host "✅ Cleanup complete" -ForegroundColor Green
}

# Register cleanup on exit
Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
    Stop-AllServers
}

# Initial server start
$backendStarted = Start-BackendServer
$frontendStarted = Start-FrontendServer

if (-not $backendStarted -or -not $frontendStarted) {
    Write-Host "❌ Failed to start one or more servers. Exiting." -ForegroundColor Red
    Stop-AllServers
    exit 1
}

Write-Host "`n🎉 All servers started successfully!" -ForegroundColor Green
Write-Host "📱 Frontend: http://localhost:$FrontendPort" -ForegroundColor White
Write-Host "🔌 Backend:  http://localhost:$BackendPort" -ForegroundColor White

# Main monitoring loop
try {
    $restartCount = 0
    while ($true) {
        Start-Sleep -Seconds $CheckInterval

        $health = Test-ServerHealth

        # Show status
        $backendIcon = if ($health.Backend) { "✅" } else { "❌" }
        $frontendIcon = if ($health.Frontend) { "✅" } else { "❌" }

        Write-Host "[$($health.Timestamp)] $backendIcon Backend | $frontendIcon Frontend" -ForegroundColor Gray

        # Auto-restart if needed and enabled
        if (-not $NoRestart) {
            if (-not $health.Backend) {
                Write-Host "🔄 Backend down, restarting..." -ForegroundColor Yellow
                Start-BackendServer | Out-Null
                $restartCount++
            }

            if (-not $health.Frontend) {
                Write-Host "🔄 Frontend down, restarting..." -ForegroundColor Yellow
                Start-FrontendServer | Out-Null
                $restartCount++
            }

            if ($restartCount -gt 10) {
                Write-Host "⚠️ Too many restarts ($restartCount). There may be a persistent issue." -ForegroundColor Red
                $restartCount = 0
            }
        }
    }
}
catch {
    Write-Host "`n🛑 Monitoring stopped" -ForegroundColor Red
}
finally {
    Stop-AllServers
}
