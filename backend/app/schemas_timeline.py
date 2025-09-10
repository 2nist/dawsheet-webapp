from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class TempoMark(BaseModel):
    atSec: float = Field(..., description="Absolute second where this tempo becomes active")
    bpm: float


class TimeSigMark(BaseModel):
    atSec: float
    num: int
    den: int


class Section(BaseModel):
    kind: str = Field(..., description="Normalized section type (Verse, Chorus, Bridge, etc.)")
    startSec: float
    endSec: Optional[float] = None
    name: Optional[str] = None
    inferred: Optional[bool] = False


class ChordEvent(BaseModel):
    symbol: str
    atSec: float
    atBeat: float
    durationBeats: Optional[float] = None
    lyricId: Optional[str] = None


class LyricEvent(BaseModel):
    id: str
    atSec: float
    atBeat: float
    text: str


class SongTimeline(BaseModel):
    id: str
    title: Optional[str] = None
    artist: Optional[str] = None
    bpmDefault: float
    timeSigDefault: dict
    tempoMap: List[TempoMark]
    timeSigMap: List[TimeSigMark]
    sections: List[Section]
    chords: List[ChordEvent]
    lyrics: List[LyricEvent]
    key: Optional[str] = None
    mode: Optional[str] = None


class TimelineWarning(BaseModel):
    code: str
    message: str


class TimelineResponse(BaseModel):
    timeline: SongTimeline
    warnings: List[TimelineWarning]


class TimelineDebugResponse(BaseModel):
    songId: int
    counts: dict
    lastBeat: float
    sample: dict
    warnings: List[TimelineWarning]
    validation: List[TimelineWarning]
