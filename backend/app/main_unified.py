from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .routers import songs, import_router

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(songs.router, prefix=settings.api_v1_prefix)
app.include_router(import_router.router, prefix=settings.api_v1_prefix)

@app.get("/")
async def root():
    return {"message": "DAWSheet API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Legacy compatibility endpoints for existing frontend
@app.get("/songs")
async def legacy_songs():
    """Legacy endpoint for backward compatibility"""
    from .repositories.song_repository import song_repository
    return song_repository.get_all()

@app.post("/songs")
async def legacy_create_song(song_data: dict):
    """Legacy endpoint for backward compatibility"""
    from .repositories.song_repository import song_repository
    from .models.song import SongCreate
    song_create = SongCreate(**song_data)
    return song_repository.create(song_create)

@app.post("/import/json")
async def legacy_import_json(data: dict):
    """Legacy endpoint for backward compatibility"""
    from .repositories.song_repository import song_repository
    from .services.import_isophonics import normalize_isophonics_data, from_isophonics

    try:
        normalized_data = normalize_isophonics_data(data)
        song = from_isophonics(normalized_data)

        song_create_data = {
            "title": song.title,
            "artist": song.artist,
            "content": song.content,
            "metadata": song.metadata
        }

        created_song = song_repository.create(song_create_data)
        return {"success": True, "song_id": created_song.id, "message": "Song imported successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/parse")
async def legacy_parse_text(data: dict):
    """Legacy endpoint for text parsing"""
    from .repositories.song_repository import song_repository
    from .models.song import SongCreate

    text = data.get("text", "")
    lines = text.strip().split('\n')
    title = lines[0] if lines else "Text Import"

    song_create = SongCreate(
        title=title,
        artist="Text Import",
        content=text
    )

    created_song = song_repository.create(song_create)
    return {"success": True, "song_id": created_song.id}
