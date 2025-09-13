Development Guide & Server Management
===============================================

## 🚀 Quick Start (Recommended)

**For reliable, auto-restarting servers:**
```powershell
.\robust-servers.ps1
```

**To check server status anytime:**
```powershell
.\check-servers.ps1
```

## ⚠️ Common Issue: Servers Start Then Stop

If you've been experiencing servers that start but then crash/stop repeatedly, this is usually caused by:

1. **Docker Desktop interference** - containers or WSL2 networking conflicts
2. **Port conflicts** - other processes using ports 8000/3000
3. **Memory/resource limits** - system running out of resources
4. **File watcher issues** - too many files being watched causing crashes

## 🛠️ Permanent Solution

The new `robust-servers.ps1` script solves these issues by:

- **Auto-monitoring**: Checks server health every 5 seconds
- **Auto-restart**: Immediately restarts crashed servers
- **Port cleanup**: Kills conflicting processes before starting
- **Health checking**: Tests actual HTTP endpoints, not just ports
- **Graceful shutdown**: Properly cleans up on exit

## 📋 Server Management Commands

```powershell
# Start servers with auto-restart (recommended)
.\robust-servers.ps1

# Start servers without auto-restart
.\robust-servers.ps1 -NoRestart

# Use custom ports
.\robust-servers.ps1 -BackendPort 8001 -FrontendPort 3001

# Check server status
.\check-servers.ps1
```

## 🔍 Troubleshooting

### Servers won't stay running
- Use `.\robust-servers.ps1` instead of `.\start-servers.ps1`
- The robust script will automatically restart crashed servers

### Port conflicts
- Run `.\check-servers.ps1` to see what's using your ports
- Use custom ports: `.\robust-servers.ps1 -BackendPort 8001 -FrontendPort 3001`

### Docker Desktop Issues
-----------------
1) Stop Docker Desktop temporarily to free ports and run services locally:

   PowerShell:

   ```powershell
   # stops WSL 2 and Docker engine
   wsl --shutdown

   # start backend locally
   .\scripts\dev-backend.ps1

   # start frontend locally (in a separate shell)
   .\scripts\dev-frontend.ps1
   ```

2) Or run the API inside Docker and frontend locally (keeps DB in container):

   ```powershell
   docker compose up -d api
   cd web
   npm run dev
   ```

3) If ports are already taken, run servers on alternate ports:

   - Backend: `./scripts/dev-backend.ps1 -Port 8001`
   - Frontend: `./scripts/dev-frontend.ps1 -Port 3001`

When Docker Desktop won't start or the engine pipe is missing
------------------------------------------------------------
- Try restarting Docker Desktop from the GUI (System tray icon → Troubleshoot → Restart Docker Desktop)
- If the Windows service `com.docker.service` is stopped and cannot be started, try rebooting Windows or reinstalling Docker Desktop.
- Use `wsl --shutdown` to clear WSL state (this can resolve stuck docker-desktop WSL issues). Then open Docker Desktop GUI to re-start the engine.

If you'd like, I can continue diagnosing your Docker Desktop logs and WSL state and recommend specific settings (WSL2 resources, file sharing, or switching to Docker Desktop stable). Ask me to "run Docker diagnostics" and I'll collect the logs and suggest the exact fix.
