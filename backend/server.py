from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import new unified components
try:
    from app.core.config import settings
    from app.routers import songs, import_router
    from app.repositories.song_repository import song_repository
    from app.models.song import SongCreate
    from app.services.import_isophonics import normalize_isophonics_data, from_isophonics
    unified_backend_available = True
except ImportError as e:
    print(f"Warning: Unified backend components not available: {e}")
    unified_backend_available = False
    # Fallback settings
    class Settings:
        backend_cors_origins = ["*"]
        api_v1_prefix = "/api/v1"
        debug = True
    settings = Settings()

# Import legacy routers for backward compatibility
try:
    from routers import library, analyze, export_ as export_router, bridge
    legacy_routers_available = True
except ImportError:
    legacy_routers_available = False

app = FastAPI(
    title="DAWSheet API",
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

# Include new unified routers
if unified_backend_available:
    app.include_router(songs.router, prefix=settings.api_v1_prefix, tags=["songs"])
    app.include_router(import_router.router, prefix=settings.api_v1_prefix, tags=["import"])

# Include legacy routers if available
if legacy_routers_available:
    app.include_router(library.router, prefix="/api/library", tags=["library"])
    app.include_router(analyze.router, prefix="/api/analyze", tags=["analyze"])
    app.include_router(export_router.router, prefix="/api/export", tags=["export"])
    app.include_router(bridge.router, prefix="/api/bridge", tags=["bridge"])

# Serve frontend static files (only if directory exists)
try:
    app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
except Exception:
    # Frontend directory not found, skip mounting
    pass

@app.get("/")
async def root():
    return {"message": "DAWSheet API", "version": "1.0.0"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}

# Legacy compatibility endpoints for existing frontend
@app.get("/songs")
async def legacy_songs():
    """Legacy endpoint for backward compatibility"""
    if unified_backend_available:
        return song_repository.get_all()
    else:
        return []

@app.post("/songs")
async def legacy_create_song(song_data: dict):
    """Legacy endpoint for backward compatibility"""
    if unified_backend_available:
        song_create = SongCreate(**song_data)
        return song_repository.create(song_create)
    else:
        return {"error": "Unified backend not available"}

@app.post("/import/json")
async def legacy_import_json(data: dict):
    """Legacy endpoint for backward compatibility"""
    if not unified_backend_available:
        return {"success": False, "error": "Unified backend not available"}

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
    if not unified_backend_available:
        return {"success": False, "error": "Unified backend not available"}

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
