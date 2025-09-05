from __future__ import annotations
import csv
import re
from dataclasses import dataclass
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
    for raw in text.splitlines():
        m = ts_vtt_re.match(raw.strip())
        if m:
            hh, mm, ss, ms = map(int, m.groups()[:4])
            cur_ts = hh * 3600 + mm * 60 + ss + ms / 1000.0
            continue
        clean = raw.strip()
        if clean:
            lines.append(LineOut(text=clean, ts=cur_ts))
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


def parse_lyrics_payload(text: str, filename: Optional[str] = None) -> List[LineOut]:
    name = (filename or "").lower()
    if name.endswith(".lrc"):
        return _parse_lrc(text)
    if name.endswith(".vtt") or "WEBVTT" in text[:20].upper():
        return _parse_vtt(text)
    if name.endswith(".csv"):
        return _parse_csv(text)
    # default plain text
    return _parse_txt(text)
