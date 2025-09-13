from __future__ import annotations

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..services.lyrics_providers.lrclib import search_timestamped_lyrics
from ..config import settings

router = APIRouter(tags=["lyrics"])


@router.get("/search")
async def lyrics_search(
    title: str = Query(..., min_length=1),
    artist: str = Query(..., min_length=1),
    album: Optional[str] = None,
    duration_sec: Optional[int] = Query(default=None, ge=0),
):
    if not settings.LYRICS_PROVIDER_ENABLED:
        raise HTTPException(status_code=503, detail="Lyrics provider disabled")
    try:
        result = await search_timestamped_lyrics(
            title=title, artist=artist, album=album, duration_sec=duration_sec
        )
        return result
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Lyrics provider error: {e}")
