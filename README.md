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
