# Quick Server Status Checker
# Run this to see current server status without starting anything

$BackendPort = 8000
$FrontendPort = 3000

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

function Get-ProcessByPort {
    param([int]$Port)
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if ($connection) {
            $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
            return $process
        }
    }
    catch {}
    return $null
}

Write-Host "🔍 Dawsheet Server Status Check" -ForegroundColor Green
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor Gray

# Check Backend
$backendPort = Test-PortInUse $BackendPort
$backendHealth = Test-Endpoint "http://localhost:$BackendPort/api/health"
$backendProcess = Get-ProcessByPort $BackendPort

Write-Host "🐍 Backend (Port $BackendPort):" -ForegroundColor Cyan
if ($backendPort) {
    Write-Host "  ✅ Port listening" -ForegroundColor Green
    if ($backendProcess) {
        Write-Host "  📊 Process: $($backendProcess.ProcessName) (PID: $($backendProcess.Id))" -ForegroundColor White
        Write-Host "  🕐 Started: $($backendProcess.StartTime)" -ForegroundColor White
    }
} else {
    Write-Host "  ❌ Port not listening" -ForegroundColor Red
}

if ($backendHealth) {
    Write-Host "  ✅ Health endpoint responding" -ForegroundColor Green
} else {
    Write-Host "  ❌ Health endpoint not responding" -ForegroundColor Red
}

# Check Frontend
$frontendPort = Test-PortInUse $FrontendPort
$frontendProcess = Get-ProcessByPort $FrontendPort

Write-Host "`n⚛️ Frontend (Port $FrontendPort):" -ForegroundColor Cyan
if ($frontendPort) {
    Write-Host "  ✅ Port listening" -ForegroundColor Green
    if ($frontendProcess) {
        Write-Host "  📊 Process: $($frontendProcess.ProcessName) (PID: $($frontendProcess.Id))" -ForegroundColor White
        Write-Host "  🕐 Started: $($frontendProcess.StartTime)" -ForegroundColor White
    }
} else {
    Write-Host "  ❌ Port not listening" -ForegroundColor Red
}

# Summary
Write-Host "`n📋 Summary:" -ForegroundColor Yellow
if ($backendPort -and $frontendPort) {
    Write-Host "  🎉 Both servers are running!" -ForegroundColor Green
    Write-Host "  📱 Frontend: http://localhost:$FrontendPort" -ForegroundColor White
    Write-Host "  🔌 Backend:  http://localhost:$BackendPort" -ForegroundColor White
} elseif ($backendPort -or $frontendPort) {
    Write-Host "  ⚠️ Only some servers are running" -ForegroundColor Yellow
    if (-not $backendPort) { Write-Host "  📌 Need to start backend" -ForegroundColor Red }
    if (-not $frontendPort) { Write-Host "  📌 Need to start frontend" -ForegroundColor Red }
} else {
    Write-Host "  ❌ No servers running" -ForegroundColor Red
    Write-Host "  💡 Run: .\robust-servers.ps1" -ForegroundColor Cyan
}

Write-Host "`n💡 Commands:" -ForegroundColor Yellow
Write-Host "  .\robust-servers.ps1          # Start with auto-restart" -ForegroundColor White
Write-Host "  .\robust-servers.ps1 -NoRestart # Start without auto-restart" -ForegroundColor White
Write-Host "  .\check-servers.ps1           # Check status (this script)" -ForegroundColor White
