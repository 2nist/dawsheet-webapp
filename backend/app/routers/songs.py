from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.song import Song, SongCreate, SongUpdate
from ..repositories.song_repository import song_repository

router = APIRouter(prefix="/songs", tags=["songs"])

@router.get("/", response_model=List[Song])
async def list_songs():
    """Get all songs"""
    return song_repository.get_all()

@router.post("/", response_model=Song)
async def create_song(song: SongCreate):
    """Create a new song"""
    return song_repository.create(song)

@router.get("/{song_id}", response_model=Song)
async def get_song(song_id: int):
    """Get a specific song by ID"""
    song = song_repository.get_by_id(song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@router.put("/{song_id}", response_model=Song)
async def update_song(song_id: int, song_update: SongUpdate):
    """Update a song"""
    song = song_repository.update(song_id, song_update)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@router.delete("/{song_id}")
async def delete_song(song_id: int):
    """Delete a song"""
    success = song_repository.delete(song_id)
    if not success:
        raise HTTPException(status_code=404, detail="Song not found")
    return {"message": "Song deleted successfully"}

@router.post("/{song_id}/copy", response_model=Song)
async def copy_song(song_id: int):
    """Create a copy of an existing song"""
    copied_song = song_repository.copy(song_id)
    if not copied_song:
        raise HTTPException(status_code=404, detail="Song not found")
    return copied_song
