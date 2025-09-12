# DAWSheet Web App (FastAPI + Next.js)

## 🚀 Quick Deployment

### Option 1: One-Click Deployment (Recommended)
Double-click `deploy.bat` or run in PowerShell:
```powershell
.\deploy.bat
```

### Option 2: Manual Setup
1. **Backend API Server:**
   ```powershell
   .venv\Scripts\python.exe backend\server_simple.py
   ```

2. **Frontend Development Server:**
   ```powershell
   cd web
   npm run dev
   ```

## 🌐 Application URLs

- **Frontend App**: http://localhost:3001 (or next available port)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/api/health

## 🐳 Docker Deployment (Alternative)

Quick start for local dev on Windows with PowerShell:

1. Start everything with Docker
   - Requires Docker Desktop.
   - In this folder (`webapp`), run:

```powershell
# from webapp/
docker compose up --build
```

2. Open the app

- API: http://localhost:8000/docs
- Web: http://localhost:3000

## 📥 Import Flow & Testing

### ✅ Comprehensive Test Suite
Run the full backend test suite:
```powershell
.venv\Scripts\python.exe test_unified_backend.py
```

This tests:
- ✅ Health endpoints
- ✅ CRUD operations (Create, Read, Update, Delete, Copy)
- ✅ Import functionality (Isophonics format, JSON, text)
- ✅ Legacy endpoint compatibility

### 🎵 Test Data
The application includes Beatles song test data:
- `test_data/hey_jude.json`
- `test_data/let_it_be.json`
- `test_data/yesterday.json`

### 🏗️ Architecture

**Backend (FastAPI):**
- **Unified API**: `backend/server_simple.py` - Complete standalone server
- **Modular Structure**: `backend/app/` - Organized models, repositories, services
- **CRUD Operations**: Full Create, Read, Update, Delete, Copy for songs
- **Import System**: Supports Isophonics format with normalization
- **Legacy Compatibility**: Maintains backward compatibility with existing endpoints

**Frontend (Next.js 14):**
- **4-Tab Interface**: Library, Timeline, Record, Editor
- **Drag & Drop**: File import with SWR refresh
- **State Management**: Zustand for global state
- **Responsive Design**: Mobile-friendly interface

### 🔧 Development Commands

```powershell
# Install dependencies
cd web && npm install

# Run tests
.venv\Scripts\python.exe -m pytest tests/

# Check API health
curl http://localhost:8000/api/health

# View API documentation
# Open http://localhost:8000/docs in browser
```

## 🛠️ Troubleshooting

- **Port conflicts**: Backend uses 8000, frontend uses 3001 (or next available)
- **Python environment**: Ensure `.venv` is activated
- **Node.js**: Requires Node.js 18+ for Next.js 14
- **Dependencies**: Run `npm install` in `/web` directory if frontend fails

- Go to http://localhost:3000/import
- Paste sample text and click Parse & Save.
- View songs at http://localhost:3000/songs

Notes

- The API proxies parsing to your Cloud Run `/parse` endpoint.
- Database uses Postgres in Docker. Change credentials in `docker-compose.yml` as needed.
- For production, deploy API to Cloud Run/Render and Web to Vercel/Render; point NEXT_PUBLIC_API_BASE accordingly.

### UI data fetching

- Uses native `fetch` behind a tiny data layer (`web/lib/api.ts`) and SWR for UI caching/state. Axios removed.
- SWR fetcher: `swrFetcher` returns JSON; mutations use `postJSON`, `putJSON`, `del` helpers.

### Legacy sandbox flag

- Gate `/legacy` with `NEXT_PUBLIC_ENABLE_LEGACY=true` (client + middleware) or `ENABLE_LEGACY=true` (server env).
- If disabled, navigating to `/legacy` redirects to `/` and the page shows a hint.

## Incremental Integration Log

- [TBD] Foundation setup (no runtime changes)

- 2025-09-05 Imported curated docs/samples/tools; no runtime changes.
- 2025-09-05 Imported curated docs/samples/tools; no runtime changes.
- 2025-09-05 – Legacy foundation skeleton + smoke test; no runtime changes.
