@echo off
echo 🚀 Quick Server Restart for Dawsheet
echo.

echo Stopping existing servers...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 >nul

echo.
echo Starting Backend Server...
cd /d "C:\Users\CraftAuto-Sales\dawsheet\webapp"
start "Backend" cmd /k "python minimal_server.py"

echo.
echo Starting Frontend Server...
cd /d "C:\Users\CraftAuto-Sales\dawsheet\webapp\web"
start "Frontend" cmd /k "npm run dev"

echo.
echo ✅ Servers starting...
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo.
echo Press any key to exit...
pause >nul
