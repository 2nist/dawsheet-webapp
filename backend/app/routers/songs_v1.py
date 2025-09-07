from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any, Dict

from ..database import get_session
from .. import models
from ..services.analysis import analyze_songdoc, analyze_from_content

router = APIRouter(prefix="/v1/songs", tags=["songs_v1"])


@router.get("/{song_id}/doc")
async def get_song_doc(song_id: int = Path(..., ge=1), session: AsyncSession = Depends(get_session)):
	result = await session.execute(select(models.Song).where(models.Song.id == song_id))
	song = result.scalar_one_or_none()
	if not song:
		raise HTTPException(status_code=404, detail="Song not found")
	analyzed = analyze_from_content(song.title, song.artist, song.content or "")
	return analyzed

