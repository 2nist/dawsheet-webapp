from fastapi import APIRouter, Body
from .schemas_song import LegacyLine, LegacySection, LegacySong, LegacyChord

router = APIRouter()


@router.get("/ping")
def ping():
    return {"ok": True, "service": "legacy"}


@router.post("/lyrics/parse")
def parse_lyrics(raw: str = Body(..., media_type="text/plain")):
    # Simple stub: split into lines; no chord parsing yet
    lines = []
    for line in raw.splitlines():
        line = line.strip("\r\n")
        if line == "":
            continue
        lines.append(LegacyLine(text=line, chords=None))
    section = LegacySection(name="Body", lines=lines)
    song = LegacySong(title="Untitled", artist="", content=raw, sections=[section])
    return {"songs": [song]}
