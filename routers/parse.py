from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from pydantic import BaseModel, Field


# Local SongRecord/Event definitions to avoid circular imports with webapp.server
class Event(BaseModel):
    beat_abs: float = Field(..., alias='beat_abs')
    time_s: float
    timecode: str | None = None
    chord: str
    section: str | None = None
    dur_beats: float | None = None
    dur_s: float | None = None
    lyric: str | None = None
    event_id: str | None = None


class SongRecord(BaseModel):
    id: str
    title: str
    artist: str | None = None
    source: str | None = None
    project_id: str | None = None
    events: List[Event]

router = APIRouter()


@router.post('/parse/midi')
async def parse_midi(file: UploadFile = File(...)):
    # simple implementation: use mido to extract tempo map and markers
    try:
        import mido
    except Exception:
        raise HTTPException(status_code=500, detail='mido not installed')
    data = await file.read()
    from io import BytesIO
    mid = mido.MidiFile(file=BytesIO(data))
    events = []
    t = 0
    for track in mid.tracks:
        time_acc = 0
        for msg in track:
            time_acc += msg.time
            if msg.type == 'marker' or msg.type == 'lyrics' or msg.type == 'note_on':
                # simplified mapping
                events.append({ 'beat_abs': time_acc, 'time_s': time_acc * 0.001, 'chord': 'N/A'})
    sr = SongRecord(id='upload-mid', title=file.filename, events=[Event(**e) for e in events[:50]])
    return sr.dict()


@router.post('/parse/musicxml')
async def parse_musicxml(file: UploadFile = File(...)):
    try:
        import music21 as m21
    except Exception:
        raise HTTPException(status_code=500, detail='music21 not installed')
    data = await file.read()
    s = m21.converter.parseBytes(data)
    events = []
    # naive: extract measures and chords
    for el in s.recurse().getElementsByClass(m21.chord.Chord):
        events.append({'beat_abs': float(el.offset), 'time_s': float(el.offset), 'chord': el.pitchedCommonName})
    sr = SongRecord(id='upload-mxl', title=file.filename, events=[Event(**e) for e in events[:100]])
    return sr.dict()


@router.post('/parse/lab')
async def parse_lab(file: UploadFile = File(...)):
    data = (await file.read()).decode('utf-8')
    events = []
    for line in data.splitlines():
        line = line.strip()
        if not line or line.startswith('#'): continue
        parts = line.split()
        try:
            time_s = float(parts[0])
            label = parts[1] if len(parts)>1 else 'N/A'
            events.append({'beat_abs': time_s, 'time_s': time_s, 'chord': label})
        except Exception:
            continue
    sr = SongRecord(id='upload-lab', title='lab', events=[Event(**e) for e in events[:200]])
    return sr.dict()
