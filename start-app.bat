@echo OFF
echo Starting Docker Desktop...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

echo Waiting for Docker to start...
timeout /t 30 /nobreak

echo Starting the DAW-Sheet application...
docker-compose up -d

echo Application is starting in the background. It might take a minute for everything to be ready.
echo Frontend will be available at http://localhost:3000
echo Backend API will be available at http://localhost:8000

echo Launching the web browser...
start http://localhost:3000
