from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import re

router = APIRouter()


class LyricLine(BaseModel):
    line: int
    startSec: float | None = None
    endSec: float | None = None
    text: str
    conf: str | None = None


def parse_lrc_bytes(b: bytes) -> List[LyricLine]:
    s = b.decode('utf-8', errors='ignore')
    pattern = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\](.*)")
    lines: List[LyricLine] = []
    idx = 0
    for l in s.splitlines():
        m = pattern.match(l)
        if m:
            mm = int(m.group(1))
            ss = float(m.group(2))
            text = m.group(3).strip()
            start = mm * 60 + ss
            lines.append(LyricLine(line=idx, startSec=start, endSec=None, text=text, conf='high'))
            idx += 1
    return lines


def parse_txt_bytes(b: bytes) -> List[LyricLine]:
    s = b.decode('utf-8', errors='ignore')
    lines: List[LyricLine] = []
    for i, l in enumerate([x for x in s.splitlines() if x.strip()]):
        lines.append(LyricLine(line=i, startSec=None, endSec=None, text=l.strip(), conf='low'))
    return lines


@router.post('/parse/lyrics/lrc')
async def parse_lrc(file: UploadFile = File(...)):
    data = await file.read()
    try:
        out = parse_lrc_bytes(data)
        return [o.dict() for o in out]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/parse/lyrics/txt')
async def parse_txt(file: UploadFile = File(...)):
    data = await file.read()
    try:
        out = parse_txt_bytes(data)
        return [o.dict() for o in out]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
