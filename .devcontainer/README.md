# Dev Container (VS Code)

This dev container attaches to the existing docker-compose stack and opens the workspace in the `api` service (Python 3.11) with Node 20 available, so you can develop both FastAPI and Next.js.

## How it works

- Uses docker-compose.yml services (db, api, web)
- The editor runs in the `api` container at `/app` (which is mounted to `backend/` and the repo root via compose volume)
- Node 20 is installed via devcontainer features so you can run `npm` for the web app from the dev container

## First-time

- Command Palette → Dev Containers: Reopen in Container
- After build, postCreate installs Python deps (`backend/requirements.txt`) and Node deps (`web/`)

## Common commands

- API dev server is already started by compose (uvicorn with reload)
- From terminal in container:
  - `cd web && npm run dev` to launch Next.js on port 3000
  - `pytest -q` to run API tests

## Ports

- 8000 FastAPI, 3000 Next.js, 5432 Postgres (forwarded)

If you want the editor to attach to `web` instead, change `service` to `web` in devcontainer.json.
