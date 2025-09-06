from fastapi import APIRouter, Body, Request
from .ingest.lyrics import parse_lyrics_payload

router = APIRouter()


@router.get("/ping")
def ping():
    return {"ok": True, "service": "legacy"}


@router.post("/lyrics/parse")
async def parse_lyrics(request: Request, filename: str | None = None):
    # Support both text/plain and application/json bodies
    ctype = request.headers.get("content-type", "")
    if "application/json" in ctype:
        payload = await request.body()
        raw = payload.decode("utf-8", errors="ignore")
    else:
        raw = await request.body()
        raw = raw.decode("utf-8", errors="ignore")
    lines = parse_lyrics_payload(raw, filename)
    # Force SongDoc-like shape for UI: {lines:[{ts?,text}]}
    return {
        "lines": [{"text": l.text, **({"ts": l.ts} if l.ts is not None else {})} for l in lines],
        "sections": None,
    }
