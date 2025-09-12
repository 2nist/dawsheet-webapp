"""
Simplified DAWSheet Backend Server
Unified architecture with proper imports
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import json

# Simple in-memory storage
songs_storage = {}

# Pydantic Models
class SongBase(BaseModel):
    title: str
    artist: str = ""
    content: str = ""
    metadata: Dict[str, Any] = {}

class SongCreate(SongBase):
    pass

class SongUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class Song(SongBase):
    id: str
    created_at: datetime
    updated_at: datetime

class ImportRequest(BaseModel):
    data: Dict[str, Any]
    format: str = "auto"

# Initialize FastAPI app
app = FastAPI(
    title="DAWSheet API",
    version="1.0.0",
    description="Unified DAWSheet Backend API"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions
def create_song_id() -> str:
    return str(uuid.uuid4())

def normalize_isophonics_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Isophonics format data"""
    if "metadata" in data:
        return data

    # Convert legacy format
    normalized = {
        "metadata": {
            "title": data.get("title", "Unknown Title"),
            "artist": data.get("artist", "Unknown Artist"),
            "duration": data.get("duration", 0)
        },
        "chords": data.get("chords", []),
        "lyrics": data.get("lyrics", {}),
        "structure": data.get("structure", [])
    }

    return normalized

def isophonics_to_song(data: Dict[str, Any]) -> SongCreate:
    """Convert Isophonics data to Song"""
    normalized = normalize_isophonics_data(data)
    metadata = normalized["metadata"]

    # Create content from chords and lyrics
    content_parts = []
    if normalized.get("chords"):
        content_parts.append(f"Chords: {len(normalized['chords'])} items")
    if normalized.get("lyrics"):
        content_parts.append(f"Lyrics: {normalized['lyrics']}")
    if normalized.get("structure"):
        content_parts.append(f"Structure: {len(normalized['structure'])} sections")

    return SongCreate(
        title=metadata["title"],
        artist=metadata["artist"],
        content=" | ".join(content_parts) if content_parts else json.dumps(normalized),
        metadata=normalized
    )

# API Routes
@app.get("/")
async def root():
    return {"message": "DAWSheet API", "version": "1.0.0"}

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

# Songs CRUD
@app.get("/api/v1/songs", response_model=List[Song])
async def list_songs():
    return list(songs_storage.values())

@app.post("/api/v1/songs", response_model=Song)
async def create_song(song: SongCreate):
    song_id = create_song_id()
    now = datetime.now()

    new_song = Song(
        id=song_id,
        title=song.title,
        artist=song.artist,
        content=song.content,
        metadata=song.metadata,
        created_at=now,
        updated_at=now
    )

    songs_storage[song_id] = new_song
    return new_song

@app.get("/api/v1/songs/{song_id}", response_model=Song)
async def get_song(song_id: str):
    if song_id not in songs_storage:
        raise HTTPException(status_code=404, detail="Song not found")
    return songs_storage[song_id]

@app.put("/api/v1/songs/{song_id}", response_model=Song)
async def update_song(song_id: str, song_update: SongUpdate):
    if song_id not in songs_storage:
        raise HTTPException(status_code=404, detail="Song not found")

    song = songs_storage[song_id]
    update_data = song_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(song, field, value)

    song.updated_at = datetime.now()
    return song

@app.delete("/api/v1/songs/{song_id}")
async def delete_song(song_id: str):
    if song_id not in songs_storage:
        raise HTTPException(status_code=404, detail="Song not found")

    del songs_storage[song_id]
    return {"message": "Song deleted successfully"}

@app.post("/api/v1/songs/{song_id}/copy", response_model=Song)
async def copy_song(song_id: str):
    if song_id not in songs_storage:
        raise HTTPException(status_code=404, detail="Song not found")

    original = songs_storage[song_id]
    copy_id = create_song_id()
    now = datetime.now()

    copied_song = Song(
        id=copy_id,
        title=f"Copy of {original.title}",
        artist=original.artist,
        content=original.content,
        metadata=original.metadata.copy() if original.metadata else {},
        created_at=now,
        updated_at=now
    )

    songs_storage[copy_id] = copied_song
    return copied_song

# Import endpoints
@app.post("/api/v1/import/isophonics")
async def import_isophonics(request: ImportRequest):
    try:
        song_data = isophonics_to_song(request.data)
        song = await create_song(song_data)
        return {"success": True, "song_id": song.id, "message": "Song imported successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")

@app.post("/api/v1/import/json")
async def import_json(request: ImportRequest):
    return await import_isophonics(request)

@app.post("/api/v1/import/text")
async def import_text(data: Dict[str, str]):
    text = data.get("text", "")
    lines = text.strip().split('\n')
    title = lines[0] if lines else "Text Import"

    song_data = SongCreate(
        title=title,
        artist="Text Import",
        content=text
    )

    song = await create_song(song_data)
    return {"success": True, "song_id": song.id, "message": "Text imported successfully"}

# Legacy compatibility endpoints
@app.get("/songs")
async def legacy_songs():
    return list(songs_storage.values())

@app.post("/songs")
async def legacy_create_song(song_data: dict):
    song_create = SongCreate(**song_data)
    return await create_song(song_create)

@app.post("/import/json")
async def legacy_import_json(data: dict):
    try:
        request = ImportRequest(data=data)
        result = await import_isophonics(request)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/parse")
async def legacy_parse_text(data: dict):
    try:
        result = await import_text(data)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

# Add some demo data
@app.on_event("startup")
async def startup_event():
    """Add demo songs on startup"""
    demo_songs = [
        SongCreate(
            title="Demo Song 1",
            artist="Demo Artist",
            content="This is a demo song for testing",
            metadata={"demo": True, "genre": "Demo"}
        ),
        SongCreate(
            title="Demo Song 2",
            artist="Another Artist",
            content="Another demo song with different content",
            metadata={"demo": True, "genre": "Test"}
        )
    ]

    for song_data in demo_songs:
        await create_song(song_data)

    print(f"✅ Added {len(demo_songs)} demo songs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
