#!/usr/bin/env powershell
<#
.SYNOPSIS
    DAWSheet Application Deployment Script
.DESCRIPTION
    This script starts both the backend API server and frontend development server
    for the DAWSheet web application.
#>

param(
    [switch]$StopOnly,
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

# Configuration
$WEBAPP_ROOT = "C:\Users\CraftAuto-Sales\dawsheet\webapp"
$PYTHON_EXE = "$WEBAPP_ROOT\.venv\Scripts\python.exe"
$BACKEND_SCRIPT = "$WEBAPP_ROOT\backend\server_simple.py"
$FRONTEND_DIR = "$WEBAPP_ROOT\web"

# Colors for output
$ErrorColor = "Red"
$SuccessColor = "Green"
$InfoColor = "Cyan"
$WarningColor = "Yellow"

function Write-ColorOutput {
    param($Message, $Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Stop-Servers {
    Write-ColorOutput "🛑 Stopping all servers..." $InfoColor

    # Kill Python processes
    try {
        taskkill /F /IM python.exe 2>$null
        Write-ColorOutput "✅ Stopped Python processes" $SuccessColor
    } catch {
        Write-ColorOutput "⚠️ No Python processes to stop" $WarningColor
    }

    # Kill Node processes
    try {
        taskkill /F /IM node.exe 2>$null
        Write-ColorOutput "✅ Stopped Node processes" $SuccessColor
    } catch {
        Write-ColorOutput "⚠️ No Node processes to stop" $WarningColor
    }

    Start-Sleep 2
}

function Start-Backend {
    Write-ColorOutput "🚀 Starting DAWSheet Backend API Server..." $InfoColor

    # Change to webapp root directory
    Set-Location $WEBAPP_ROOT

    # Start backend server in background
    $backendJob = Start-Job -ScriptBlock {
        param($PythonExe, $BackendScript, $WebappRoot)
        Set-Location $WebappRoot
        & $PythonExe $BackendScript
    } -ArgumentList $PYTHON_EXE, $BACKEND_SCRIPT, $WEBAPP_ROOT

    Write-ColorOutput "✅ Backend server starting (Job ID: $($backendJob.Id))" $SuccessColor
    Write-ColorOutput "📍 Backend API: http://localhost:8000" $InfoColor
    Write-ColorOutput "📖 API Docs: http://localhost:8000/docs" $InfoColor

    # Wait a moment for startup
    Start-Sleep 3

    # Test backend health
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 5
        if ($response.status -eq "healthy") {
            Write-ColorOutput "✅ Backend health check passed" $SuccessColor
        }
    } catch {
        Write-ColorOutput "⚠️ Backend health check failed - server may still be starting" $WarningColor
    }

    return $backendJob
}

function Start-Frontend {
    Write-ColorOutput "🌐 Starting DAWSheet Frontend Server..." $InfoColor

    # Change to frontend directory
    Set-Location $FRONTEND_DIR

    # Start frontend server in background
    $frontendJob = Start-Job -ScriptBlock {
        param($FrontendDir)
        Set-Location $FrontendDir
        npm run dev
    } -ArgumentList $FRONTEND_DIR

    Write-ColorOutput "✅ Frontend server starting (Job ID: $($frontendJob.Id))" $SuccessColor
    Write-ColorOutput "🌍 Frontend URL: http://localhost:3001 (or first available port)" $InfoColor

    return $frontendJob
}

function Show-Status {
    Write-ColorOutput "`n📊 Application Status:" $InfoColor
    Write-ColorOutput "=" * 50 $InfoColor

    # Check running jobs
    $jobs = Get-Job
    if ($jobs) {
        Write-ColorOutput "Background Jobs:" $InfoColor
        foreach ($job in $jobs) {
            $status = if ($job.State -eq "Running") { "✅" } else { "❌" }
            Write-ColorOutput "  $status Job $($job.Id): $($job.State)" $InfoColor
        }
    }

    # Test endpoints
    Write-ColorOutput "`nEndpoint Tests:" $InfoColor

    # Backend health
    try {
        $backendHealth = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 3
        if ($backendHealth.status -eq "healthy") {
            Write-ColorOutput "  ✅ Backend API: http://localhost:8000 (Healthy)" $SuccessColor
        }
    } catch {
        Write-ColorOutput "  ❌ Backend API: http://localhost:8000 (Not responding)" $ErrorColor
    }

    # Frontend (basic connectivity)
    try {
        $frontendTest = Invoke-WebRequest -Uri "http://localhost:3001" -TimeoutSec 3 -UseBasicParsing
        if ($frontendTest.StatusCode -eq 200) {
            Write-ColorOutput "  ✅ Frontend: http://localhost:3001 (Running)" $SuccessColor
        }
    } catch {
        # Try port 3000 as fallback
        try {
            $frontendTest = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 3 -UseBasicParsing
            if ($frontendTest.StatusCode -eq 200) {
                Write-ColorOutput "  ✅ Frontend: http://localhost:3000 (Running)" $SuccessColor
            }
        } catch {
            Write-ColorOutput "  ❌ Frontend: Not responding on port 3000 or 3001" $ErrorColor
        }
    }

    Write-ColorOutput "`n🎯 Quick Links:" $InfoColor
    Write-ColorOutput "  • Application: http://localhost:3001" $InfoColor
    Write-ColorOutput "  • API Documentation: http://localhost:8000/docs" $InfoColor
    Write-ColorOutput "  • API Health: http://localhost:8000/api/health" $InfoColor
}

# Main execution
try {
    Write-ColorOutput "🎵 DAWSheet Application Deployment" $InfoColor
    Write-ColorOutput "=" * 50 $InfoColor

    if ($StopOnly) {
        Stop-Servers
        Write-ColorOutput "✅ All servers stopped" $SuccessColor
        exit 0
    }

    # Stop existing servers first
    Stop-Servers

    # Start servers based on parameters
    $jobs = @()

    if (!$FrontendOnly) {
        $backendJob = Start-Backend
        $jobs += $backendJob
    }

    if (!$BackendOnly) {
        $frontendJob = Start-Frontend
        $jobs += $frontendJob
    }

    # Wait for servers to start
    Write-ColorOutput "`n⏳ Waiting for servers to start..." $InfoColor
    Start-Sleep 5

    # Show status
    Show-Status

    Write-ColorOutput "`n🎉 DAWSheet application is ready!" $SuccessColor
    Write-ColorOutput "Press Ctrl+C to stop all servers, or close this window." $InfoColor

    # Keep script running to monitor jobs
    try {
        while ($true) {
            Start-Sleep 10

            # Check if any jobs have failed
            $failedJobs = Get-Job | Where-Object { $_.State -eq "Failed" -or $_.State -eq "Stopped" }
            if ($failedJobs) {
                Write-ColorOutput "`n⚠️ Some services have stopped:" $WarningColor
                foreach ($job in $failedJobs) {
                    Write-ColorOutput "  Job $($job.Id): $($job.State)" $ErrorColor
                    # Show job output for debugging
                    $output = Receive-Job $job
                    if ($output) {
                        Write-ColorOutput "  Output: $output" $ErrorColor
                    }
                }
                break
            }
        }
    } catch {
        Write-ColorOutput "`n🛑 Shutting down..." $InfoColor
    }

} catch {
    Write-ColorOutput "❌ Error: $($_.Exception.Message)" $ErrorColor
    exit 1
} finally {
    # Cleanup jobs
    Get-Job | Remove-Job -Force 2>$null
}

Write-ColorOutput "👋 DAWSheet deployment script finished" $InfoColor
