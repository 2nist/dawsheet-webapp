from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from ..legacy.ingest.lyrics import parse_lyrics_payload


router = APIRouter(prefix="/import", tags=["import"])


@router.post("/lyrics")
async def import_lyrics(file: UploadFile = File(...)):
    """Parse a single lyrics file (.txt, .lrc, .vtt, .csv, .json) and return
    normalized entries with optional timestamps.

    Response shape focuses on UI-friendly preview/testing:
    {
      "items": [{"section": null | str, "line": str, "timestamp": float | null}],
      "filename": str,
      "size_bytes": int
    }
    Also includes a "lines" alias for backward-compat preview UIs: [{"text","ts"}].
    """
    fname = file.filename or ""
    try:
        raw = await file.read()
        text = raw.decode("utf-8", errors="ignore")
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")

    lines = parse_lyrics_payload(text, fname)

    items = [
        {
            "section": None,
            "line": l.text,
            **({"timestamp": float(l.ts)} if l.ts is not None else {"timestamp": None}),
        }
        for l in lines
    ]

    # legacy alias used by existing preview UI
    lines_alias = [
        {"text": it["line"], **({"ts": it["timestamp"]} if it["timestamp"] is not None else {})}
        for it in items
    ]

    return JSONResponse(
        {
            "ok": True,
            "filename": fname,
            "size_bytes": len(raw),
            "items": items,
            "lines": lines_alias,
        }
    )
