import re
from typing import List, Dict, Tuple


_SEP_RE = re.compile(r"^\s*([-=#*_])\1{2,}\s*$")
_CHORDPRO_TITLE_RE = re.compile(r"^\s*\{\s*(title|t)\s*:\s*(.*?)\s*}\s*$", re.IGNORECASE)
_CHORDPRO_ARTIST_RE = re.compile(r"^\s*\{\s*(artist|subtitle|st)\s*:\s*(.*?)\s*}\s*$", re.IGNORECASE)


def _normalize(text: str) -> str:
    # Normalize line endings and quotes
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u2018", "'").replace("\u2019", "'").replace("\u201C", '"').replace("\u201D", '"')
    # Trim trailing whitespace lines
    lines = [ln.rstrip() for ln in text.split("\n")]
    return "\n".join(lines).strip()


def _split_songs(text: str) -> List[str]:
    lines = text.split("\n")
    chunks: List[List[str]] = []
    buf: List[str] = []
    title_hits = 0
    for ln in lines:
        if _CHORDPRO_TITLE_RE.match(ln):
            title_hits += 1
            if title_hits > 1 and buf:
                chunks.append(buf)
                buf = []
        elif _SEP_RE.match(ln) and buf:
            # separator line: treat as split if we already have some content buffered
            chunks.append(buf)
            buf = []
            continue
        buf.append(ln)
    if buf:
        chunks.append(buf)
    if not chunks:
        return [text]
    return ["\n".join(c).strip() for c in chunks if any(t.strip() for t in c)]


def _guess_title_artist(lines: List[str]) -> Tuple[str, str]:
    title = ""
    artist = ""
    for ln in lines[:10]:  # inspect first few lines only
        m = _CHORDPRO_TITLE_RE.match(ln)
        if m:
            title = m.group(2)
            continue
        m = _CHORDPRO_ARTIST_RE.match(ln)
        if m:
            artist = m.group(2)
            continue
        if not title and ":" in ln and ln.lower().startswith("title:"):
            title = ln.split(":", 1)[1].strip()
        if not artist and ":" in ln and ln.lower().startswith("artist:"):
            artist = ln.split(":", 1)[1].strip()
        if not title and " - " in ln and len(ln.split(" - ", 1)[0]) <= 120:
            t, a = ln.split(" - ", 1)
            if not artist:
                artist = a.strip()
            title = t.strip()
        if title and artist:
            break
    # Fallback to first non-empty line as title
    if not title:
        for ln in lines:
            s = ln.strip()
            if s and not s.startswith("#") and not s.startswith("//"):
                title = s[:120]
                break
    return title or "Untitled", artist or ""


def parse_songs(raw: str) -> List[Dict[str, str]]:
    text = _normalize(raw)
    parts = _split_songs(text)
    songs: List[Dict[str, str]] = []
    for part in parts:
        lines = part.split("\n")
        title, artist = _guess_title_artist(lines)
        songs.append({
            "title": title,
            "artist": artist,
            "content": part.strip(),
        })
    return songs
