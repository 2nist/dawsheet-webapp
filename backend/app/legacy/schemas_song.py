from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel


class LegacyChord(BaseModel):
    name: str


class LegacyLine(BaseModel):
    text: str
    chords: Optional[List[LegacyChord]] = None


class LegacySection(BaseModel):
    name: str
    lines: List[LegacyLine]


class LegacySong(BaseModel):
    title: str
    artist: Optional[str] = ""
    content: str
    sections: Optional[List[LegacySection]] = None
