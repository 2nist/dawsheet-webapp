from __future__ import annotations

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any, Dict, Optional

from ..database import get_session
from .. import models, schemas
from ..utils.align import merge_jcrd_with_lyrics, chords_only_text
from ..services.lyrics_providers.lrclib import search_timestamped_lyrics
from ..config import settings

router = APIRouter(prefix="/combine", tags=["combine"])


@router.post("/jcrd-lyrics")
async def combine_jcrd_lyrics(
    payload: Dict[str, Any] = Body(...),
    save: Optional[bool] = None,
    session: AsyncSession = Depends(get_session),
):
    """Combine JCRD-like chord JSON and lyrics lines into a master song.
    Payload shape:
    { jcrd: {...}, lyrics: { lines: [{ ts_sec: number|null, text: str }, ...] }, title?: str, artist?: str }
    """
    jcrd = payload.get("jcrd")
    lyrics = payload.get("lyrics") or {}
    if not isinstance(jcrd, dict) or not isinstance(lyrics, dict):
        raise HTTPException(status_code=400, detail="Invalid payload: require jcrd and lyrics objects")
    include_lyrics = payload.get("include_lyrics")
    if include_lyrics is None:
        include_lyrics = True
    bar_start = str(payload.get("bar_start") or "auto").lower()
    if bar_start not in ("auto", "zero"):
        bar_start = "auto"
    lines = lyrics.get("lines") or []
    if not isinstance(lines, list):
        raise HTTPException(status_code=400, detail="Invalid lyrics.lines")
    # Auto-fetch lyrics if requested to include and no lines provided
    if include_lyrics and not lines:
        if settings.LYRICS_PROVIDER_ENABLED:
            title = (payload.get("title") or jcrd.get("metadata", {}).get("title") or "").strip()
            artist = (payload.get("artist") or jcrd.get("metadata", {}).get("artist") or "").strip()
            if title:
                try:
                    fetched = await search_timestamped_lyrics(title=title, artist=artist)
                    if fetched and isinstance(fetched.get("lines"), list):
                        lines = fetched["lines"]
                except Exception:
                    # Ignore provider failures; will fallback to chords only if still no lines
                    pass
        # else provider disabled; proceed with empty lines

    if include_lyrics:
        merged = merge_jcrd_with_lyrics(jcrd, lines, bar_start=bar_start)
    else:
        merged = chords_only_text(jcrd, bar_start=bar_start)
    title = (payload.get("title") or jcrd.get("metadata", {}).get("title") or "Untitled").strip()
    artist = (payload.get("artist") or jcrd.get("metadata", {}).get("artist") or "").strip()

    result = {"title": title, "artist": artist, **merged}

    if save:
        song = models.Song(user_id=1, title=title, artist=artist, content=merged.get("content", ""))  # type: ignore[index]
        session.add(song)
        await session.commit()
        await session.refresh(song)
        result["song"] = {"id": song.id, "title": song.title, "artist": song.artist}

    return result
