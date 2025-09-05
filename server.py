from __future__ import annotations
from typing import List
import os

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from dawsheet.io.sheets import SheetsClient
from fastapi import APIRouter
from webapp.routers import parse as parse_router
from webapp.routers import hints as hints_router

app = FastAPI(title='DAWSheet Internal API')

# include parse router
app.include_router(parse_router.router, prefix="")
app.include_router(hints_router.router, prefix="")


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


@app.get('/healthz')
def healthz():
    return {'status': 'ok'}


@app.post('/import/songrecord', status_code=202)
def import_songrecord(record: SongRecord, sheet_id: str | None = Query(None), tab: str = Query('Timeline')):
    # Resolve spreadsheet id
    sid = sheet_id or os.getenv('DAWSHEET_SPREADSHEET_ID') or ''
    if not sid:
        raise HTTPException(status_code=400, detail='spreadsheet id required')
    client = SheetsClient(spreadsheet_id=sid)
    # Convert events to dict rows keyed by canonical HEADERS where possible
    rows = []
    for ev in record.events:
        r = {
            'ProjectId': record.project_id or record.id,
            'EventId': ev.event_id or '',
            'BeatAbs': ev.beat_abs,
            'Time_s': ev.time_s,
            'Timecode': ev.timecode or '',
            'Chord': ev.chord,
            'Section': ev.section or '',
            'Dur_beats': ev.dur_beats or '',
            'Dur_s': ev.dur_s or '',
            'Lyric': ev.lyric or '',
            'Source': record.source or 'api',
        }
        rows.append(r)
    try:
        written = client.append_rows(tab, rows)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {'written': written}
