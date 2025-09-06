from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import json

router = APIRouter(prefix="/import", tags=["import"])


@router.post("/json")
async def import_json(file: UploadFile = File(...)):
    # Basic guardrails
    if not (file.filename or "").lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="Please upload a .json file")

    try:
        raw = await file.read()
        data = json.loads(raw.decode("utf-8", errors="ignore"))
    except Exception as e:  # noqa: BLE001 - return error to client
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    summary = _summarize_json(data)

    return JSONResponse(
        {
            "ok": True,
            "filename": file.filename,
            "size_bytes": len(raw),
            "summary": summary,
            "preview": data if isinstance(data, dict) else {"root_type": type(data).__name__},
        }
    )


def _summarize_json(data):
    if isinstance(data, dict):
        keys = list(data.keys())[:12]
        return {"type": "object", "keys_sample": keys, "total_keys": len(data)}
    if isinstance(data, list):
        t = type(data[0]).__name__ if data else "empty"
        return {"type": "array", "len": len(data), "first_item_type": t}
    return {"type": type(data).__name__}
