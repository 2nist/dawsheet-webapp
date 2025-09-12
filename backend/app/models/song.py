from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChordItem(BaseModel):
    id: str
    beat: float
    symbol: str
    duration: float = 4.0

class LyricItem(BaseModel):
    id: str
    beat: float
    text: str
    duration: float = 1.0

class Section(BaseModel):
    id: str
    name: str
    start_beat: float
    length_beats: float
    color: str = "#8B5CF6"

class Lane(BaseModel):
    id: str
    type: str  # "chords", "lyrics", "melody", etc.
    name: str
    items: List[Dict[str, Any]] = []

class SongMetadata(BaseModel):
    key: Optional[str] = "C"
    tempo: Optional[int] = 120
    time_signature: Optional[str] = "4/4"
    genre: Optional[str] = None
    year: Optional[int] = None

class Song(BaseModel):
    id: Optional[int] = None
    title: str
    artist: str
    content: str = ""
    metadata: SongMetadata = SongMetadata()
    sections: List[Section] = []
    lanes: List[Lane] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SongCreate(BaseModel):
    title: str
    artist: str
    content: str = ""
    metadata: Optional[SongMetadata] = None

class SongUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[SongMetadata] = None
    sections: Optional[List[Section]] = None
    lanes: Optional[List[Lane]] = None

class ImportRequest(BaseModel):
    data: Dict[str, Any]
    format: str = "isophonics"
    include_analysis: bool = True
