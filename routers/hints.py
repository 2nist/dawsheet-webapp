from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class KeyHintRequest(BaseModel):
    songId: Optional[str]
    sectionId: Optional[str]
    chords: List[str]


class KeyHintResponse(BaseModel):
    key: str
    mode: str
    confidence: float


def normalize_chord(ch: str) -> str:
    # strip extensions like Cmaj7 -> C, Am7 -> A
    if not ch: return ''
    ch = ch.strip()
    # root is first char(s) with optional #/b
    m = ch[0]
    if len(ch) > 1 and ch[1] in ['#','b']:
        m = ch[:2]
    return m.upper()


@router.post('/hint/key_chroma', response_model=KeyHintResponse)
async def key_chroma(req: KeyHintRequest):
    if not req.chords:
        raise HTTPException(status_code=400, detail='no chords provided')
    counts = {}
    total = 0
    for c in req.chords:
        root = normalize_chord(c)
        if not root: continue
        counts[root] = counts.get(root, 0) + 1
        total += 1
    if total == 0:
        raise HTTPException(status_code=400, detail='no valid chord roots')
    # pick most frequent root
    best = max(counts.items(), key=lambda kv: kv[1])
    key = best[0]
    confidence = best[1] / total
    # naive mode detection: if minor chords (m/a) appear often, mark minor
    minor_count = sum(1 for c in req.chords if 'm' in c.lower() and not c.lower().startswith('m'))
    mode = 'minor' if minor_count / max(1, total) > 0.4 else 'major'
    return KeyHintResponse(key=key, mode=mode, confidence=round(confidence, 3))
