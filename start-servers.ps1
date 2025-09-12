# Robust server startup script for Dawsheet
Write-Host "🚀 Starting Dawsheet Servers..." -ForegroundColor Green

# Kill any existing processes
Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
try { taskkill /F /IM python.exe 2>$null } catch { }
try { taskkill /F /IM node.exe 2>$null } catch { }
Start-Sleep -Seconds 2

# Function to check if port is available
function Test-Port {
    param($Port)
    $result = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
    return -not $result
}

# Function to start backend with retry
function Start-Backend {
    Write-Host "🐍 Starting Backend Server (Port 8000)..." -ForegroundColor Cyan

    if (Test-Port 8000) {
        $backendJob = Start-Job -ScriptBlock {
            Set-Location "C:\Users\CraftAuto-Sales\dawsheet\webapp"
            python minimal_server.py
        }

        # Wait a bit and check if it started
        Start-Sleep -Seconds 3
        if (Test-Port 8000) {
            Write-Host "❌ Backend failed to start" -ForegroundColor Red
            return $false
        } else {
            Write-Host "✅ Backend running on http://localhost:8000" -ForegroundColor Green
            return $true
        }
    } else {
        Write-Host "⚠️ Port 8000 already in use" -ForegroundColor Yellow
        return $true
    }
}

# Function to start frontend with retry
function Start-Frontend {
    Write-Host "⚛️ Starting Frontend Server..." -ForegroundColor Cyan

    $frontendJob = Start-Job -ScriptBlock {
        Set-Location "C:\Users\CraftAuto-Sales\dawsheet\webapp\web"
        npm run dev
    }

    # Wait for frontend to start
    $timeout = 30
    $elapsed = 0
    do {
        Start-Sleep -Seconds 1
        $elapsed++
        $portCheck = netstat -ano | findstr ":3000"
        if ($portCheck) {
            Write-Host "✅ Frontend running on http://localhost:3000" -ForegroundColor Green
            return $true
        }
    } while ($elapsed -lt $timeout)

    Write-Host "❌ Frontend failed to start within $timeout seconds" -ForegroundColor Red
    return $false
}

# Start servers
$backendStarted = Start-Backend
$frontendStarted = Start-Frontend

if ($backendStarted -and $frontendStarted) {
    Write-Host "🎉 All servers started successfully!" -ForegroundColor Green
    Write-Host "📱 Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "🔌 Backend:  http://localhost:8000" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Ctrl+C to stop all servers" -ForegroundColor Yellow

    # Keep script running
    try {
        while ($true) {
            Start-Sleep -Seconds 5
            # Quick health check
            if (Test-Port 8000 -or Test-Port 3000) {
                Write-Host "⚠️ Server(s) may have crashed. Consider restarting." -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "🛑 Shutting down servers..." -ForegroundColor Red
    }
} else {
    Write-Host "❌ Failed to start servers" -ForegroundColor Red
    exit 1
}
