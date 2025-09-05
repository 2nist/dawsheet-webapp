# Migrations (Alembic)

- With Docker: migrations run automatically on API start (`alembic upgrade head`).
- Without Docker (local):
  1. Ensure Postgres is running (docker compose up db).
  2. Set `DATABASE_URL` (e.g., `postgresql+psycopg://dawsheet:dawsheet@localhost:5432/dawsheet`).
  3. From `webapp/backend` run:

```powershell
# from webapp/backend
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL="postgresql+psycopg://dawsheet:dawsheet@localhost:5432/dawsheet"
alembic -c alembic.ini upgrade head
```
