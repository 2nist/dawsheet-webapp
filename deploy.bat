@echo off
:: DAWSheet Application Deployment Script
:: Starts both backend API and frontend servers

title DAWSheet Application Server

echo.
echo =======================================
echo   DAWSheet Application Deployment
echo =======================================
echo.

:: Set paths
set WEBAPP_ROOT=%~dp0
set PYTHON_EXE=%WEBAPP_ROOT%.venv\Scripts\python.exe
set BACKEND_SCRIPT=%WEBAPP_ROOT%backend\server_simple.py
set FRONTEND_DIR=%WEBAPP_ROOT%web

:: Change to webapp root
cd /d "%WEBAPP_ROOT%"

:: Stop any existing processes
echo Stopping existing servers...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 >nul

:: Start backend server
echo Starting backend API server...
start "DAWSheet Backend" /B "%PYTHON_EXE%" "%BACKEND_SCRIPT%"

:: Wait for backend to start
echo Waiting for backend to start...
timeout /t 5 >nul

:: Test backend health
powershell -Command "try { $r = Invoke-RestMethod 'http://localhost:8000/api/health' -TimeoutSec 5; if ($r.status -eq 'healthy') { Write-Host 'Backend health check: PASSED' -ForegroundColor Green } } catch { Write-Host 'Backend health check: FAILED (server may still be starting)' -ForegroundColor Yellow }"

:: Start frontend server
echo Starting frontend development server...
cd /d "%FRONTEND_DIR%"
start "DAWSheet Frontend" cmd /k "npm run dev"

:: Show information
echo.
echo =======================================
echo   DAWSheet Application Ready!
echo =======================================
echo.
echo Backend API:      http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Frontend App:     http://localhost:3001 (or next available port)
echo.
echo Press any key to stop all servers...
pause >nul

:: Stop servers
echo Stopping servers...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1

echo.
echo Servers stopped. Goodbye!
timeout /t 2 >nul
