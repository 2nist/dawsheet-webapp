"""
Ultra-Stable DAWSheet Backend Server
Minimal FastAPI server with better error handling and stability
"""
import sys
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import json
import uvicorn

# Simple in-memory storage
songs_storage = {}

print("🚀 Initializing DAWSheet Backend...")

# Pydantic Models
class SongBase(BaseModel):
    title: str
    artist: str = ""
    content: str = ""
    metadata: Dict[str, Any] = {}

class SongCreate(SongBase):
    pass

class Song(SongBase):
    id: str
    created_at: datetime
    updated_at: datetime

# Initialize FastAPI app
app = FastAPI(
    title="DAWSheet API",
    version="1.0.0",
    description="Stable DAWSheet Backend API"
)

print("✅ FastAPI app created")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("✅ CORS middleware added")

# Helper functions
def create_song_id() -> str:
    return str(uuid.uuid4())

def add_demo_songs():
    """Add demo songs to storage"""
    demo_songs = [
        {
            "title": "Stable Demo Song 1",
            "artist": "Demo Artist",
            "content": "This is a stable demo song",
            "metadata": {"demo": True, "stable": True}
        },
        {
            "title": "Stable Demo Song 2",
            "artist": "Another Artist",
            "content": "Another stable demo song",
            "metadata": {"demo": True, "stable": True}
        }
    ]

    for song_data in demo_songs:
        song_id = create_song_id()
        now = datetime.now()

        new_song = Song(
            id=song_id,
            title=song_data["title"],
            artist=song_data["artist"],
            content=song_data["content"],
            metadata=song_data["metadata"],
            created_at=now,
            updated_at=now
        )

        songs_storage[song_id] = new_song

    print(f"✅ Added {len(demo_songs)} demo songs")

# API Routes
@app.get("/")
async def root():
    return {"message": "DAWSheet Stable API", "version": "1.0.0", "status": "running"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "songs_count": len(songs_storage)}

@app.get("/health")
async def health_simple():
    return {"status": "ok"}

# Songs CRUD
@app.get("/api/v1/songs")
async def list_songs():
    try:
        return list(songs_storage.values())
    except Exception as e:
        print(f"Error in list_songs: {e}")
        return []

@app.post("/api/v1/songs")
async def create_song(song: SongCreate):
    try:
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
    except Exception as e:
        print(f"Error in create_song: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create song: {str(e)}")

@app.get("/api/v1/songs/{song_id}")
async def get_song(song_id: str):
    try:
        if song_id not in songs_storage:
            raise HTTPException(status_code=404, detail="Song not found")
        return songs_storage[song_id]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_song: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get song: {str(e)}")

# Legacy compatibility endpoints
@app.get("/songs")
async def legacy_songs():
    try:
        return list(songs_storage.values())
    except Exception as e:
        print(f"Error in legacy_songs: {e}")
        return []

@app.post("/songs")
async def legacy_create_song(song_data: dict):
    try:
        song_create = SongCreate(**song_data)
        return await create_song(song_create)
    except Exception as e:
        print(f"Error in legacy_create_song: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create song: {str(e)}")

# Add demo data on startup
try:
    add_demo_songs()
    print("✅ Demo data loaded successfully")
except Exception as e:
    print(f"❌ Error loading demo data: {e}")

def main():
    """Main entry point"""
    try:
        print("🌐 Starting DAWSheet Stable Server...")
        print("📍 Backend will be available at: http://localhost:8000")
        print("📖 API docs will be available at: http://localhost:8000/docs")
        print("🔧 Health check: http://localhost:8000/api/health")

        # Run with uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
