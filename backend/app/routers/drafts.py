from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
from ..database import get_session
from .. import models

router = APIRouter(tags=["drafts"])

@router.get("/jobs/{job_id}")
async def get_job(job_id: int, session: AsyncSession = Depends(get_session)):
    job = await session.get(models.Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    draft_db_id = None
    draft_str_id = None
    if job.status == "done":
        # Prefer: find Recording by this job, then its Draft
        rec_result = await session.execute(select(models.Recording).where(models.Recording.job_id == job.id))
        rec = rec_result.scalars().first()
        if rec:
            sd_result = await session.execute(
                select(models.SongDraft).where(models.SongDraft.recording_id == rec.id).order_by(models.SongDraft.id.desc())
            )
            sd = sd_result.scalars().first()
        else:
            # Fallback: latest draft
            rs = await session.execute(select(models.SongDraft).order_by(models.SongDraft.id.desc()))
            sd = rs.scalars().first()
        if sd:
            draft_db_id = sd.id
            draft_str_id = f"draft_{sd.id}"
    return {
        "id": job.id,
        "kind": job.kind,
        "status": job.status,
        "error": job.error,
        "draftId": draft_str_id,
        "draft_db_id": draft_db_id,
    }

@router.get("/drafts/{draft_id}")
async def get_draft(draft_id: int, session: AsyncSession = Depends(get_session)):
    sd = await session.get(models.SongDraft, draft_id)
    if not sd:
        raise HTTPException(status_code=404, detail="Draft not found")
    return {
        "id": sd.id,
        "recording_id": sd.recording_id,
        "meta": json.loads(sd.meta) if sd.meta else {},
        "bpm": sd.bpm,
        "sections": json.loads(sd.sections) if sd.sections else [],
        "chords": json.loads(sd.chords) if sd.chords else [],
        "lyrics": sd.lyrics or "",
    }

def _infer_sections_with_lengths(raw_sections: list[dict], bpm: float | None) -> list[dict]:
    # Expect items like { name: str, start: number }
    sections = []
    if not raw_sections:
        return sections
    # Sort by start just in case
    ordered = sorted(raw_sections, key=lambda x: float(x.get("start") or 0))
    for i, s in enumerate(ordered):
        start_sec = float(s.get("start") or 0)
        start_beats = (start_sec * bpm / 60) if bpm else start_sec
        next_start_sec = float(ordered[i + 1].get("start")) if i + 1 < len(ordered) and ordered[i + 1].get("start") is not None else None
        
        length_beats = 8.0  # Default length in beats
        if next_start_sec is not None and next_start_sec > start_sec:
            if bpm:
                length_beats = (next_start_sec - start_sec) * bpm / 60
            else:
                length_beats = next_start_sec - start_sec

        sections.append({
            "name": s.get("name") or "Other",
            "startBeat": start_beats,
            "lengthBeats": length_beats,
            "source": "analysis",
        })
    return sections

@router.get("/drafts/{draft_id}/songdoc")
async def get_draft_songdoc(draft_id: int, session: AsyncSession = Depends(get_session)):
    """Return a SongDocDraft (v1) view of the draft, matching the provided JSON Schema shape."""
    sd = await session.get(models.SongDraft, draft_id)
    if not sd:
        raise HTTPException(status_code=404, detail="Draft not found")
    # Source info
    rec = None
    if sd.recording_id:
        rec = await session.get(models.Recording, sd.recording_id)
    meta = json.loads(sd.meta) if sd.meta else {}
    raw_sections = json.loads(sd.sections) if sd.sections else []
    chords = json.loads(sd.chords) if sd.chords else []
    lyrics_str = sd.lyrics or ""
    lines = [ln for ln in (lyrics_str.splitlines()) if ln.strip()]
    # Build draft view
    doc = {
        "v": 1,
        "draftId": f"draft_{sd.id}",
        "status": getattr(sd, "status", "draft_ready"),
        "createdAt": sd.created_at.isoformat() if getattr(sd, "created_at", None) else None,
        "updatedAt": (sd.updated_at.isoformat() if getattr(sd, "updated_at", None) else (sd.created_at.isoformat() if getattr(sd, "created_at", None) else None)),
        "source": {
            "recordingId": str(sd.recording_id) if sd.recording_id else None,
            "filePath": rec.file_path if rec else None,
            "storage": "local",
            "format": (rec.file_path.split(".")[-1].lower() if rec and rec.file_path and "." in rec.file_path else "other"),
        },
        "meta": {
            "title": meta.get("title"),
            "artist": meta.get("artist"),
            "album": meta.get("album"),
            "key": meta.get("key"),
            "mode": meta.get("mode"),
            "timeSig": meta.get("timeSig"),
            "bpm": ({"value": float(sd.bpm)} if sd.bpm else None),
        },
        "sections": _infer_sections_with_lengths(raw_sections, sd.bpm),
        "chords": [
            {
                "symbol": c.get("symbol") or c.get("chord") or "",
                "startBeat": (float(c.get("start")) * sd.bpm / 60) if sd.bpm and c.get("start") is not None else float(c.get("startBeat") or c.get("start") or 0),
                "source": c.get("source") or "analysis",
            }
            for c in (chords or [])
            if (c.get("symbol") or c.get("chord")) is not None
        ],
        "lyrics": [
            {"text": t}
            for t in lines
        ],
    "analysis": {
            "jobId": (str(rec.job_id) if rec and rec.job_id else None),
            "providers": {"id": "none", "lyrics": "none", "tempo": "other", "chords": "none"},
            "errors": [],
        },
    "notes": getattr(sd, "notes", None),
    }
    return doc

@router.post("/songs/from-draft")
async def create_song_from_draft(
    payload: dict = Body(...), session: AsyncSession = Depends(get_session)
):
    # Accept numeric ID or string like "draft_123"
    raw_id = payload.get("draftId")
    if raw_id is None:
        raise HTTPException(status_code=422, detail="draftId is required")
    if isinstance(raw_id, str) and raw_id.startswith("draft_"):
        try:
            draft_id = int(raw_id.split("_", 1)[1])
        except Exception:
            raise HTTPException(status_code=422, detail="Invalid draftId format")
    else:
        draft_id = int(raw_id)
    sd = await session.get(models.SongDraft, draft_id)
    if not sd:
        raise HTTPException(status_code=404, detail="Draft not found")
    meta = json.loads(sd.meta) if sd.meta else {}
    title = meta.get("title") or "Untitled"
    artist = meta.get("artist") or ""
    # Build a simple content from sections/chords/lyrics for now
    sections = json.loads(sd.sections) if sd.sections else []
    lines = [f"# {s.get('name')}" for s in sections]
    if sd.lyrics:
        lines.append("")
        lines.append(sd.lyrics)
    content = "\n".join(lines)
    song = models.Song(user_id=1, title=title, artist=artist, content=content)
    session.add(song)
    await session.commit()
    await session.refresh(song)
    # Update draft status/link
    sd.status = "promoted"
    sd.song_id = song.id
    await session.commit()
    return {"id": song.id, "title": song.title, "artist": song.artist, "content": song.content}

@router.get("/specs/song_draft.schema.json")
async def get_song_draft_schema():
    from ..songdoc_schema import SONG_DRAFT_SCHEMA
    return SONG_DRAFT_SCHEMA
