from fastapi import APIRouter, Body
from .ingest.lyrics import parse_lyrics_payload

router = APIRouter()


@router.get("/ping")
def ping():
    return {"ok": True, "service": "legacy"}


@router.post("/lyrics/parse")
def parse_lyrics(raw: str = Body(..., media_type="text/plain")):
    lines = parse_lyrics_payload(raw)
    # Force SongDoc-like shape for UI: {lines:[{ts?,text}]}
    return {
        "lines": [{"text": l.text, **({"ts": l.ts} if l.ts is not None else {})} for l in lines],
        "sections": None,
    }
