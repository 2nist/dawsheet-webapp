from fastapi import APIRouter, HTTPException
from ..models.import_ import ImportRequest
from dawsheet.io.sheets import SheetsClient
import os

router = APIRouter()

def _require_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise HTTPException(status_code=500, detail=f"Missing env {name}")
    return v

@router.post("")
def do_import(req: ImportRequest):
    sa = _require_env("GOOGLE_SA_JSON")
    written = {"timeline": 0, "guidedrums": 0, "metadata": 0}

    client = SheetsClient(creds_env="GOOGLE_SA_JSON", spreadsheet_id=req.sheet_id)

    # Lyrics → Timeline
    if req.layers.lyrics and req.apply and req.apply.lyrics:
        written["timeline"] += client.append_rows('Timeline', req.apply.lyrics)

    # Sections → Sections tab
    if req.layers.sections and req.apply and req.apply.sections:
        written["sections"] = client.append_rows('Sections', req.apply.sections)

    # Key/Mode → Metadata (placeholder)
    if req.layers.keymode and req.apply:
        # Example: upsert key/mode if provided in apply
        km = {}
        if km:
            client.upsert_rows('Metadata', km, key_fields=['Key'])
            written["metadata"] += 1

    # Guide Drums → GuideDrums tab
    if req.layers.drums and req.apply and req.apply.drums:
        written["guidedrums"] += client.append_rows('GuideDrums', req.apply.drums)

    return {"ok": True, "rows_written": written}
