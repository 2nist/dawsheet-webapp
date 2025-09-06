from __future__ import annotations
import csv
import re
from dataclasses import dataclass
import json
from typing import Iterable, List, Optional, Tuple


@dataclass
class LineOut:
    text: str
    ts: Optional[float] = None  # seconds


ts_lrc_re = re.compile(r"\[(\d{1,2}):(\d{2})(?:\.(\d{1,3}))?\]")
ts_vtt_re = re.compile(r"^(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s+-->\s+(\d{2}):(\d{2}):(\d{2})\.(\d{3})")


def _to_seconds(mins: int, secs: int, ms: int = 0) -> float:
    return mins * 60 + secs + ms / 1000.0


def _parse_lrc(text: str) -> List[LineOut]:
    lines: List[LineOut] = []
    for raw in text.splitlines():
        matches = list(ts_lrc_re.finditer(raw))
        if not matches:
            # no timestamp; treat as untimed line
            clean = raw.strip()
            if clean:
                lines.append(LineOut(text=clean))
            continue
        # remove all [mm:ss.xx] from text
        content = ts_lrc_re.sub("", raw).strip()
        for m in matches:
            mm = int(m.group(1) or 0)
            ss = int(m.group(2) or 0)
            ms = int((m.group(3) or "0").ljust(3, "0"))
            ts = _to_seconds(mm, ss, ms)
            lines.append(LineOut(text=content, ts=ts))
    return lines


def _parse_vtt(text: str) -> List[LineOut]:
    lines: List[LineOut] = []
    cur_ts: Optional[float] = None
    started = False  # flip to True after the first timing cue
    for raw in text.splitlines():
        s = raw.strip()
        m = ts_vtt_re.match(s)
        if m:
            hh, mm, ss, ms = map(int, m.groups()[:4])
            cur_ts = hh * 3600 + mm * 60 + ss + ms / 1000.0
            started = True
            continue
        if not started:
            # Ignore headers/notes before first cue (e.g., 'WEBVTT')
            continue
        if s and not s.upper().startswith("NOTE"):
            lines.append(LineOut(text=s, ts=cur_ts))
    return lines


def _parse_txt(text: str) -> List[LineOut]:
    out: List[LineOut] = []
    for raw in text.splitlines():
        clean = raw.strip()
        if clean:
            out.append(LineOut(text=clean))
    return out


def _parse_csv(text: str) -> List[LineOut]:
    out: List[LineOut] = []
    reader = csv.reader(text.splitlines())
    for row in reader:
        if not row:
            continue
        if len(row) == 1:
            out.append(LineOut(text=row[0].strip()))
        else:
            # assume first col may be time like mm:ss.xx or seconds
            ts_val: Optional[float] = None
            t0 = row[0].strip()
            if re.match(r"^\d{1,2}:\d{2}(?:\.\d{1,3})?$", t0):
                mm, ss = t0.split(":")
                ssp, msp = (ss.split(".") + ["0"])[:2]
                ts_val = _to_seconds(int(mm), int(ssp), int(msp.ljust(3, "0")))
            else:
                try:
                    ts_val = float(t0)
                except ValueError:
                    ts_val = None
            text_col = row[1].strip() if len(row) > 1 else ""
            if text_col:
                out.append(LineOut(text=text_col, ts=ts_val))
    return out


def _parse_json(text: str) -> List[LineOut]:
    """Best-effort JSON lyrics extractor.
    Supports shapes like:
    - {"lines": ["text", ...]}
    - {"lines": [{"text":"...", "ts": 1.23}, ...]}
    - {"lyrics": "multi\nline\ntext"}
    - {"lyrics": ["line1", "line2"]}
    """
    out: List[LineOut] = []
    try:
        data = json.loads(text)
    except Exception:
        return out
    def _maybe_time(val) -> Optional[float]:
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str) and re.match(r"^\d{1,2}:\d{2}(?:\.\d{1,3})?$", val):
            mm, ss = val.split(":")
            ssp, msp = (ss.split(".") + ["0"])[:2]
            return _to_seconds(int(mm), int(ssp), int(msp.ljust(3, "0")))
        return None

    def _extract(obj, budget=[0]) -> List[LineOut]:
        # budget to avoid excessive recursion
        if budget[0] > 5000:
            return []
        budget[0] += 1
        acc: List[LineOut] = []
        # Direct known shapes
        if isinstance(obj, dict):
            # Common container keys potentially holding arrays of lines/events
            for key in (
                "lines",
                "lyrics",
                "items",
                "events",
                "segments",
                "captions",
                "subtitles",
            ):
                if key in obj and isinstance(obj[key], list):
                    acc.extend(_extract(obj[key], budget))
            # Also inspect nested dicts
            for v in obj.values():
                if isinstance(v, (dict, list)):
                    acc.extend(_extract(v, budget))
            return acc
        if isinstance(obj, list):
            for it in obj:
                if isinstance(it, str):
                    t = it.strip()
                    if t:
                        acc.append(LineOut(text=t))
                    continue
                if isinstance(it, dict):
                    # Try to read a text and time-like pair from typical keys
                    text_keys = ("text", "lyric", "line", "caption")
                    time_keys = ("ts", "time", "time_sec", "seconds", "start")
                    tval = None
                    for tk in text_keys:
                        if tk in it and isinstance(it[tk], (str, int, float)):
                            tval = str(it[tk]).strip()
                            if tval:
                                break
                    if tval:
                        ts_val: Optional[float] = None
                        for sk in time_keys:
                            if sk in it:
                                ts_val = _maybe_time(it[sk])
                                if ts_val is not None:
                                    break
                        acc.append(LineOut(text=tval, ts=ts_val))
                        continue
                    # Otherwise, recurse
                    acc.extend(_extract(it, budget))
                elif isinstance(it, (list,)):
                    acc.extend(_extract(it, budget))
            return acc
        return acc

    # Known direct shapes
    if isinstance(data, dict) and isinstance(data.get("lines"), list):
        out.extend(_extract(data["lines"]))
        return out
    # lyrics as string
    if isinstance(data, dict) and isinstance(data.get("lyrics"), str):
        return _parse_txt(data["lyrics"])
    # lyrics as list of strings
    if isinstance(data, dict) and isinstance(data.get("lyrics"), list):
        tmp = "\n".join([str(x) for x in data["lyrics"]])
        return _parse_txt(tmp)
    # Generic extraction fallback
    out.extend(_extract(data))
    return out


def parse_lyrics_payload(text: str, filename: Optional[str] = None) -> List[LineOut]:
    name = (filename or "").lower()
    if name.endswith(".lrc"):
        return _parse_lrc(text)
    if name.endswith(".vtt") or "WEBVTT" in text[:20].upper():
        return _parse_vtt(text)
    if name.endswith(".csv"):
        return _parse_csv(text)
    if name.endswith(".json") or name.endswith(".jcrd.json") or text.strip().startswith("{"):
        return _parse_json(text)
    # default plain text
    return _parse_txt(text)
