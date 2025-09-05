from pydantic import BaseModel
from typing import List, Optional

class LineIn(BaseModel):
    text: str
    chords: Optional[list] = None

class SectionIn(BaseModel):
    name: str
    lines: List[LineIn]

class SongIn(BaseModel):
    title: str
    artist: Optional[str] = ""
    content: str
    sections: Optional[List[SectionIn]] = None

class SongOut(BaseModel):
    id: int
    title: str
    artist: str
    content: str

class SongUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    content: Optional[str] = None

class ParseResponse(BaseModel):
    songs: List[SongIn]
    warnings: Optional[List[str]] = None
