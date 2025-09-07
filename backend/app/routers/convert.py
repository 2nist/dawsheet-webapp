from __future__ import annotations

from fastapi import APIRouter, Body, HTTPException
from typing import Any, Dict

from ..utils.tempo import convert_jcrd as _convert_jcrd

router = APIRouter(prefix="/convert", tags=["convert"])


@router.post("/jcrd")
def convert_jcrd_endpoint(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    try:
        return _convert_jcrd(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Conversion failed: {e}")
