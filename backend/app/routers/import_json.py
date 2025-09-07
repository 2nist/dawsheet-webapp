from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import json
from typing import Optional
from .combine import combine_jcrd_lyrics

router = APIRouter(prefix="/import", tags=["import"])


@router.post("/json")
async def import_json(file: UploadFile = File(...), include_lyrics: Optional[bool] = Query(default=True)):
    # Basic guardrails
    if not (file.filename or "").lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="Please upload a .json file")

    try:
        raw = await file.read()
        data = json.loads(raw.decode("utf-8", errors="ignore"))
    except Exception as e:  # noqa: BLE001 - return error to client
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    summary = _summarize_json(data)

    preview = data if isinstance(data, dict) else {"root_type": type(data).__name__}

    # If JCRD-like JSON, attempt to auto-combine with lyrics by default (non-destructive preview)
    result = {
        "ok": True,
        "filename": file.filename,
        "size_bytes": len(raw),
        "summary": summary,
        "preview": preview,
    }
    try:
        if isinstance(preview, dict) and (preview.get("chord_progression") or preview.get("sections")):
            # Use internal function to combine (without saving) honoring include_lyrics
            payload = {
                "jcrd": preview,
                "lyrics": {},
                "title": (preview.get("metadata", {}) or {}).get("title"),
                "artist": (preview.get("metadata", {}) or {}).get("artist"),
                "include_lyrics": include_lyrics,
            }
            combined = await combine_jcrd_lyrics(payload, save=False)  # type: ignore[arg-type]
            result["auto_combined"] = combined
    except Exception:
        # Swallow auto-combine errors; still return summary/preview
        pass

    return JSONResponse(result)


def _summarize_json(data):
    def _pick_title_artist(obj: dict):
        title = obj.get("title") or obj.get("name") or ""
        artist = obj.get("artist") or obj.get("composer") or ""
        return str(title).strip(), str(artist).strip()

    if isinstance(data, dict):
        title, artist = _pick_title_artist(data)
        # jcrd-style metadata
        meta = data.get("metadata") if isinstance(data.get("metadata"), dict) else None
        if meta:
            mt, ma = _pick_title_artist(meta)
            title = title or mt
            artist = artist or ma
        out = {
            "type": "object",
            "keys_sample": list(data.keys())[:12],
            "total_keys": len(data),
        }
        if title:
            out["title"] = title
        if artist:
            out["artist"] = artist
        if meta:
            if meta.get("tempo") is not None:
                out["tempo"] = meta.get("tempo")
            if meta.get("time_signature") is not None:
                out["time_signature"] = meta.get("time_signature")
        # If songs array exists, peek first item for hints
        if isinstance(data.get("songs"), list) and data["songs"]:
            first = data["songs"][0]
            if isinstance(first, dict):
                ft, fa = _pick_title_artist(first)
                out.setdefault("title", ft)
                out.setdefault("artist", fa)
        return out
    if isinstance(data, list):
        t = type(data[0]).__name__ if data else "empty"
        out = {"type": "array", "len": len(data), "first_item_type": t}
        if data and isinstance(data[0], dict):
            ft = str(data[0].get("title") or data[0].get("name") or "").strip()
            fa = str(data[0].get("artist") or data[0].get("composer") or "").strip()
            if ft:
                out["title"] = ft
            if fa:
                out["artist"] = fa
        return out
    return {"type": type(data).__name__}
