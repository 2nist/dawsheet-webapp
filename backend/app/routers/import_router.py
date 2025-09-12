from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..models.song import ImportRequest, Song
from ..services.import_isophonics import from_isophonics, normalize_isophonics_data
from ..repositories.song_repository import song_repository

router = APIRouter(prefix="/import", tags=["import"])

@router.post("/isophonics", response_model=Song)
async def import_isophonics(request: ImportRequest):
    """Import a song from Isophonics JSON format"""
    try:
        # Normalize the data first
        normalized_data = normalize_isophonics_data(request.data)

        # Convert to our Song model
        song = from_isophonics(normalized_data)

        # Save to repository
        song_create_data = {
            "title": song.title,
            "artist": song.artist,
            "content": song.content,
            "metadata": song.metadata
        }

        created_song = song_repository.create(song_create_data)

        # Update with sections and lanes
        if song.sections or song.lanes:
            update_data = {
                "sections": song.sections,
                "lanes": song.lanes
            }
            created_song = song_repository.update(created_song.id, update_data)

        return created_song

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")

@router.post("/json", response_model=Song)
async def import_json(data: Dict[str, Any]):
    """Import from generic JSON format - attempts to auto-detect format"""
    try:
        # Try to detect if it's Isophonics format
        if any(key in data for key in ["chord_progression", "sections", "metadata"]):
            normalized_data = normalize_isophonics_data(data)
            song = from_isophonics(normalized_data)
        else:
            # Fallback to simple format
            song = Song(
                title=data.get("title", "Imported Song"),
                artist=data.get("artist", "Unknown Artist"),
                content=str(data)
            )

        # Save to repository
        song_create_data = {
            "title": song.title,
            "artist": song.artist,
            "content": song.content,
            "metadata": song.metadata
        }

        created_song = song_repository.create(song_create_data)

        # Update with sections and lanes if present
        if hasattr(song, 'sections') and song.sections:
            update_data = {"sections": song.sections}
            if hasattr(song, 'lanes') and song.lanes:
                update_data["lanes"] = song.lanes
            created_song = song_repository.update(created_song.id, update_data)

        return created_song

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")

@router.post("/text")
async def import_text(text: str):
    """Parse and import text content"""
    try:
        # Simple text parsing - can be enhanced later
        lines = text.strip().split('\n')
        title = lines[0] if lines else "Text Import"

        song_create_data = {
            "title": title,
            "artist": "Text Import",
            "content": text
        }

        created_song = song_repository.create(song_create_data)
        return created_song

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Text import failed: {str(e)}")
