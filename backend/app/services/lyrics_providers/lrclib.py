from __future__ import annotations

import re
import time
from typing import List, Dict, Optional
import httpx

LRCLIB_URL = "https://lrclib.net/api/get"

# super-light cache (dev convenience)
_cache: dict[str, tuple[float, dict]] = {}
_CACHE_TTL = 60 * 10  # 10 min


def _mk_cache_key(title: str, artist: str, album: Optional[str], duration_sec: Optional[int]) -> str:
    return f"{title.strip().lower()}|{artist.strip().lower()}|{(album or '').strip().lower()}|{duration_sec or ''}"


async def search_timestamped_lyrics(
    title: str,
    artist: str,
    *,
    album: Optional[str] = None,
    duration_sec: Optional[int] = None,
    timeout: float = 8.0,
) -> Dict:
    """
    Returns:
      {
        "source": "lrclib",
        "matched": bool,
        "synced": bool,
        "lines": [{"ts_sec": float|None, "text": str}, ...],
        # "raw": {...raw lrclib doc...}
      }
    """
    key = _mk_cache_key(title, artist, album, duration_sec)
    now = time.time()
    if key in _cache and (now - _cache[key][0]) < _CACHE_TTL:
        return _cache[key][1]

    params: dict[str, str] = {
        "track_name": title,
        "artist_name": artist,
    }
    if album:
        params["album_name"] = album
    if duration_sec:
        params["duration"] = str(duration_sec)

    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.get(LRCLIB_URL, params=params)
        if r.status_code == 404:
            data = {"source": "lrclib", "matched": False, "synced": False, "lines": []}
            _cache[key] = (now, data)
            return data
        r.raise_for_status()
        doc = r.json()

    # LRCLIB fields typically include: "syncedLyrics", "plainLyrics"
    synced = bool(doc.get("syncedLyrics"))
    if synced:
        lines = parse_lrc(doc["syncedLyrics"])  # type: ignore[arg-type]
    else:
        # fallback to plain lyrics, no timestamps
        lines = [
            {"ts_sec": None, "text": line}
            for line in (doc.get("plainLyrics") or "").splitlines()
            if str(line).strip()
        ]

    data = {
        "source": "lrclib",
        "matched": True,
        "synced": synced,
        "lines": lines,
        # keep raw optional, comment in if needed
        # "raw": doc,
    }
    _cache[key] = (now, data)
    return data


_TS = re.compile(r"\[(\d{1,2}):(\d{2})(?:\.(\d{1,3}))?\]")


def parse_lrc(lrc_text: str) -> List[Dict]:
    """
    Parse LRC text like:
      [00:12.34] first line
      [00:25.10] second line
    Returns: [{ts_sec: 12.34, text: "first line"}, ...]
    """
    out: List[Dict] = []
    for raw in (lrc_text or "").splitlines():
        if not str(raw).strip():
            continue
        timestamps = list(_TS.finditer(raw))
        if not timestamps:
            # no timestamp: append as untimed line
            out.append({"ts_sec": None, "text": str(raw).strip()})
            continue
        text = _TS.sub("", raw).strip()
        for m in timestamps:
            mm = int(m.group(1))
            ss = int(m.group(2))
            g3 = m.group(3) or ""
            ms = int(g3 or 0)
            denom = 1000 if len(g3) == 3 else 100
            ts = mm * 60 + ss + ms / denom
            out.append({"ts_sec": float(ts), "text": text})
    # keep original order; LRC can have multiple stamps per line
    return out
