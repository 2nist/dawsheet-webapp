from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os, uuid, json, shutil
from ..database import get_session
from .. import models

router = APIRouter(prefix="/recordings", tags=["recordings"])

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/start")
async def start_recording():
    # In a simple flow, client will just POST the file to /upload; here we just return an ID
    return {"recordingId": str(uuid.uuid4())}

@router.post("/upload")
async def upload_recording(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    rec_id = str(uuid.uuid4())
    ext = ".webm"
    if file.filename and "." in file.filename:
        ext = os.path.splitext(file.filename)[1] or ".webm"
    dest_path = os.path.join(UPLOAD_DIR, f"{rec_id}{ext}")
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    rec = models.Recording(file_path=dest_path, mime_type=file.content_type or "audio/webm", status="uploaded")
    session.add(rec)
    await session.commit()
    await session.refresh(rec)
    # Create job and trigger background analysis stub
    job = models.Job(kind="analysis", status="pending")
    session.add(job)
    await session.commit()
    await session.refresh(job)
    rec.job_id = job.id
    rec.status = "processing"
    await session.commit()
    background.add_task(_run_analysis_stub, job.id, rec.id, dest_path)
    return {"recordingId": rec.id, "jobId": job.id}

async def _run_analysis_stub(job_id: int, rec_id: int, path: str):
    # NOTE: This is a stub that simulates analysis; replace with real pipeline later
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from ..config import settings
    engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with SessionLocal() as session:
        # Update job running
        job = await session.get(models.Job, job_id)
        if not job:
            return
        job.status = "running"
        await session.commit()
        # Fake results
        draft = {
            "meta": {"title": "Untitled", "artist": ""},
            "bpm": 120,
            "sections": [
                {"name": "Intro", "start": 0.0},
                {"name": "Verse", "start": 8.0},
                {"name": "Chorus", "start": 24.0},
            ],
            "chords": [],
            "lyrics": "",
            "recordingPath": path,
        }
        # Persist draft
        sd = models.SongDraft(recording_id=rec_id, meta=json.dumps(draft.get("meta")), bpm=draft.get("bpm"),
                              sections=json.dumps(draft.get("sections")), chords=json.dumps(draft.get("chords")),
                              lyrics=draft.get("lyrics"))
        session.add(sd)
        await session.commit()
        await session.refresh(sd)
        # Update recording and job with result
        rec = await session.get(models.Recording, rec_id)
        if rec:
            rec.status = "done"
            rec.analysis_result = json.dumps({"draftId": sd.id})
        job.status = "done"
        await session.commit()

@router.post("/finish")
async def finish_recording(recordingId: int = Body(..., embed=True), session: AsyncSession = Depends(get_session)):
    rec = await session.get(models.Recording, recordingId)
    if not rec:
        raise HTTPException(status_code=404, detail="Recording not found")
    return {"jobId": rec.job_id}
