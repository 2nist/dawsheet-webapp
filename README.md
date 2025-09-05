# DAWSheet Web App (FastAPI + Next.js)

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

3. Import flow

- Go to http://localhost:3000/import
- Paste sample text and click Parse & Save.
- View songs at http://localhost:3000/songs

Notes

- The API proxies parsing to your Cloud Run `/parse` endpoint.
- Database uses Postgres in Docker. Change credentials in `docker-compose.yml` as needed.
- For production, deploy API to Cloud Run/Render and Web to Vercel/Render; point NEXT_PUBLIC_API_BASE accordingly.

## Incremental Integration Log
- [TBD] Foundation setup (no runtime changes)

