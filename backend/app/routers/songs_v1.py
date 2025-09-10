from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any, Dict

from ..database import get_session
from .. import models
from ..services.analysis import analyze_songdoc, analyze_from_content
from ..mappers.timeline import to_timeline
from ..schemas_timeline import TimelineResponse, TimelineDebugResponse, TimelineWarning

router = APIRouter(prefix="/v1/songs", tags=["songs_v1"])


@router.get("/{song_id}/doc")
async def get_song_doc(song_id: int = Path(..., ge=1), session: AsyncSession = Depends(get_session)):
	result = await session.execute(select(models.Song).where(models.Song.id == song_id))
	song = result.scalar_one_or_none()
	if not song:
		raise HTTPException(status_code=404, detail="Song not found")
	analyzed = analyze_from_content(song.title, song.artist, song.content or "")
	return analyzed


@router.get("/{song_id}/timeline", response_model=TimelineResponse)
async def get_song_timeline(song_id: int = Path(..., ge=1), session: AsyncSession = Depends(get_session)):
	"""Return canonical timeline. 422 if structurally invalid (missing chords or lyrics)."""
	result = await session.execute(select(models.Song).where(models.Song.id == song_id))
	song = result.scalar_one_or_none()
	if not song:
		raise HTTPException(status_code=404, detail="Song not found")
	analyzed = analyze_from_content(song.title, song.artist, song.content or "")
	timeline, warnings, validation = to_timeline({**analyzed, "id": song.id})
	# If structural validation contains empty chords/lyrics, bubble as 422
	fatal_codes = {"chords.empty", "bpm.missing", "timesig.missing"}  # allow chord-only (no lyrics)
	if any(v.code in fatal_codes for v in validation):
		raise HTTPException(status_code=422, detail={
			"message": "Timeline invalid",
			"validation": [v.dict() for v in validation],
			"warnings": [w.dict() for w in warnings],
		})
	return {"timeline": timeline, "warnings": warnings}


@router.get("/{song_id}/timeline/debug", response_model=TimelineDebugResponse)
async def get_song_timeline_debug(song_id: int = Path(..., ge=1), session: AsyncSession = Depends(get_session)):
	result = await session.execute(select(models.Song).where(models.Song.id == song_id))
	song = result.scalar_one_or_none()
	if not song:
		raise HTTPException(status_code=404, detail="Song not found")
	analyzed = analyze_from_content(song.title, song.artist, song.content or "")
	timeline, warnings, validation = to_timeline({**analyzed, "id": song.id})
	# lastBeat = max lyric or chord atBeat
	last_beat = 0.0
	if timeline.chords:
		last_beat = max(last_beat, max(ch.atBeat for ch in timeline.chords))
	if timeline.lyrics:
		last_beat = max(last_beat, max(l.atBeat for l in timeline.lyrics))
	sample = {
		"chords": [c.dict() for c in timeline.chords[:5]],
		"lyrics": [l.dict() for l in timeline.lyrics[:5]],
		"sections": [s.dict() for s in timeline.sections[:3]],
	}
	return {
		"songId": song.id,
		"counts": {"chords": len(timeline.chords), "lyrics": len(timeline.lyrics), "sections": len(timeline.sections)},
		"lastBeat": round(last_beat, 4),
		"sample": sample,
		"warnings": warnings,
		"validation": validation,
	}

