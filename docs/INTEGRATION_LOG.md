# Integration Log

- 2025-09-05 M1 groundwork: Added Tailwind + tokens, /design workbench, migrated UI to native fetch + SWR, added /legacy feature flag gate (middleware + UI). Updated import page with preview.

- 2025-09-06 Styling baseline: Verified Tailwind config maps CSS variable tokens. Added App Router `/src/app/design/page.tsx` and root layout to preview colors/fonts/radii/spacing and token-driven components. Unified tokens via `src/styles/tokens.css` imported in `globals.css`. Updated `/pages/import-json.tsx` to use token-based utilities for a smoke styling pass.

- 2025-09-06 M2 import endpoints: Added `POST /import/lyrics` to accept .txt/.lrc/.vtt/.csv (and JSON fallback) and return normalized `{section,line,timestamp?}` plus `lines` alias. Added `POST /import/multi` to accept batch uploads (.json + .mid + .txt etc.), validate types, dedupe by title/artist, and return a summary and song list. Wired both routers in `backend/app/main.py`.
- 2025-09-06 Import UI: Updated `/pages/import.tsx` to use tokens, call new endpoints (`/import/lyrics`, `/import/multi`), show preview lines and import status, Poppins font preference, and cream background token.
- 2025-09-06 Tests: Added backend tests `backend/tests/test_import_lyrics.py` and `backend/tests/test_import_multi.py` for parsing and endpoints.
