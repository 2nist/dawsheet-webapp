from fastapi import FastAPI, Depends, HTTPException, Path, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from .config import settings
from .database import get_session, engine, Base, SessionLocal
from . import models, schemas
from .parser import parse_songs
from .legacy.router import router as legacy_router
from .routers import import_json as import_json_router
from .routers import import_lyrics as import_lyrics_router
from .routers import import_mixed as import_mixed_router
from .routers import import_lyrics as import_lyrics_router
from .routers import convert as convert_router
from .routers import lyrics_search as lyrics_search_router
from .routers import combine as combine_router
from .routers import songs_v1 as songs_v1_router
from .routers import recordings as recordings_router
from .routers import drafts as drafts_router
from .importers import import_json_file, import_midi_file, import_mp3_file

app = FastAPI(title="DAWSheet API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount legacy (isolated) endpoints
app.include_router(legacy_router, prefix="/legacy", tags=["legacy"])
app.include_router(import_json_router.router)
app.include_router(import_lyrics_router.router)
app.include_router(import_mixed_router.router)
app.include_router(import_lyrics_router.router)
app.include_router(convert_router.router)
app.include_router(lyrics_search_router.router)
app.include_router(combine_router.router)
app.include_router(songs_v1_router.router)
app.include_router(recordings_router.router)
app.include_router(drafts_router.router)

@app.on_event("startup")
async def on_startup():
    # Auto-create tables for dev; in prod use Alembic migrations
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Light-touch dev migration: ensure new columns exist on song_drafts
        try:
            await conn.exec_driver_sql(
                """
                ALTER TABLE song_drafts ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;
                ALTER TABLE song_drafts ADD COLUMN IF NOT EXISTS status VARCHAR(32) DEFAULT 'draft_ready';
                ALTER TABLE song_drafts ADD COLUMN IF NOT EXISTS song_id INTEGER REFERENCES songs(id);
                ALTER TABLE song_drafts ADD COLUMN IF NOT EXISTS notes TEXT;
                """
            )
        except Exception:
            # Ignore errors in dev migration
            pass
    
    # Create a default user if one doesn't exist
    async with SessionLocal() as session:
        result = await session.execute(select(models.User).where(models.User.id == 1))
        user = result.scalar_one_or_none()
        if not user:
            default_user = models.User(id=1, email="default@example.com")
            session.add(default_user)
            await session.commit()

@app.get("/")
async def health():
    return {"ok": True}

@app.post("/parse", response_model=schemas.ParseResponse)
async def parse_text(raw: str = Body(..., media_type="text/plain")):
    # First, attempt local robust parser to support many common formats quickly
    local = parse_songs(raw)
    if local and len(local) > 0:
        return {"songs": local, "warnings": None}
    # Fallback to remote parser if local cannot parse
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(settings.CLOUD_RUN_PARSE_URL, content=raw)
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Parser error {r.status_code}: {r.text}")
        return r.json()

@app.get("/songs", response_model=list[schemas.SongOut])
async def list_songs(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(models.Song))
    rows = result.scalars().all()
    return [schemas.SongOut(id=row.id, title=row.title, artist=row.artist, content=row.content) for row in rows]

@app.post("/songs", response_model=schemas.SongOut)
async def create_song(payload: schemas.SongIn, session: AsyncSession = Depends(get_session)):
    song = models.Song(user_id=1, title=payload.title, artist=payload.artist or "", content=payload.content)
    session.add(song)
    await session.commit()
    await session.refresh(song)
    return schemas.SongOut(id=song.id, title=song.title, artist=song.artist, content=song.content)

@app.post("/songs/{song_id}/attach-lyrics", response_model=schemas.SongOut)
async def attach_lyrics(song_id: int, payload: dict = Body(...), session: AsyncSession = Depends(get_session)):
    """Attach fetched lyrics lines to a song by updating its content.
    Payload: { lines: [{ ts_sec: number|null, text: string }], mode?: 'append'|'replace' }
    """
    result = await session.execute(select(models.Song).where(models.Song.id == song_id))
    song = result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    lines = payload.get("lines") or []
    mode = (payload.get("mode") or "append").lower()
    formatted = []
    for ln in lines:
        txt = str(ln.get("text") or "").strip()
        if not txt:
            continue
        ts = ln.get("ts_sec")
        prefix = f"[{ts:.2f}] " if isinstance(ts, (int, float)) else ""
        formatted.append(prefix + txt)
    block = "\n".join(formatted)
    if mode == "replace":
        song.content = block
    else:
        song.content = (song.content or "").rstrip() + ("\n\n" if song.content else "") + block
    await session.commit()
    await session.refresh(song)
    return schemas.SongOut(id=song.id, title=song.title, artist=song.artist, content=song.content)

@app.post("/import", response_model=schemas.ParseResponse)
async def import_file(file: UploadFile = File(...)):
    raw = (await file.read()).decode("utf-8", errors="replace")
    songs = parse_songs(raw)
    return {"songs": songs, "warnings": None}

@app.post("/import/files", response_model=schemas.ParseResponse)
async def import_files(files: list[UploadFile] = File(...)):
    all_songs: list[dict] = []
    warnings: list[str] = []
    for f in files:
        data = await f.read()
        name = (f.filename or "").lower()
        if name.endswith((".json",)):
            s, w = import_json_file(f.filename or "", data)
        elif name.endswith((".mid", ".midi")):
            s, w = import_midi_file(f.filename or "", data)
        elif name.endswith((".mp3",)):
            s, w = import_mp3_file(f.filename or "", data)
        else:
            # Fallback: treat as text and use general parser
            text = data.decode("utf-8", errors="replace")
            s = parse_songs(text)
            w = []
        all_songs.extend(s)
        warnings.extend(w)
    return {"songs": all_songs, "warnings": warnings or None}

@app.post("/import/stream", response_model=schemas.ParseResponse)
async def import_stream(url: str = Body(..., embed=True)):
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(url)
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Fetch error {r.status_code}")
        ctype = r.headers.get("content-type", "").lower()
        name = url.split("/")[-1]
        songs: list[dict]
        warnings: list[str]
        if "/json" in ctype or name.endswith(".json"):
            songs, warnings = import_json_file(name, r.content)
        elif "midi" in ctype or name.endswith((".mid", ".midi")):
            songs, warnings = import_midi_file(name, r.content)
        elif "mpeg" in ctype or name.endswith(".mp3"):
            songs, warnings = import_mp3_file(name, r.content)
        else:
            # treat as text
            text = r.content.decode("utf-8", errors="replace")
            songs = parse_songs(text)
            warnings = []
    return {"songs": songs, "warnings": warnings or None}

@app.get("/songs/{song_id}", response_model=schemas.SongOut)
async def get_song(song_id: int = Path(..., ge=1), session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(models.Song).where(models.Song.id == song_id))
    song = result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return schemas.SongOut(id=song.id, title=song.title, artist=song.artist, content=song.content)

@app.put("/songs/{song_id}", response_model=schemas.SongOut)
async def update_song(song_id: int, payload: schemas.SongUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(models.Song).where(models.Song.id == song_id))
    song = result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    if payload.title is not None:
        song.title = payload.title
    if payload.artist is not None:
        song.artist = payload.artist
    if payload.content is not None:
        song.content = payload.content
    await session.commit()
    await session.refresh(song)
    return schemas.SongOut(id=song.id, title=song.title, artist=song.artist, content=song.content)

@app.delete("/songs/{song_id}", status_code=204)
async def delete_song(song_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(models.Song).where(models.Song.id == song_id))
    song = result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    await session.delete(song)
    await session.commit()
    return None
