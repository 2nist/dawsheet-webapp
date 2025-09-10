from __future__ import annotations

from typing import Any, Dict, List, Tuple
from math import isfinite

from ..schemas_timeline import (
    SongTimeline,
    TimelineWarning,
    TempoMark,
    TimeSigMark,
    Section as SectionModel,
    ChordEvent as ChordEventModel,
    LyricEvent as LyricEventModel,
)

DEFAULT_BPM = 120.0
DEFAULT_SIG = (4, 4)


def _quantize(v: float, snap: float) -> float:
    if snap <= 0:
        return v
    return round(v / snap) * snap


def _beats_to_sec(beats: float, bpm: float) -> float:
    return (beats * 60.0) / bpm if bpm > 0 else beats


def _sec_to_beats(sec: float, bpm: float) -> float:
    return (sec * bpm) / 60.0 if bpm > 0 else sec


def _normalize_section_kind(name: str | None) -> str:
    if not name:
        return "Verse"
    n = name.lower()
    if "chorus" in n:
        return "Chorus"
    if "bridge" in n:
        return "Bridge"
    if "intro" in n:
        return "Intro"
    if "outro" in n:
        return "Outro"
    if "pre" in n:
        return "PreChorus"
    if "solo" in n:
        return "Solo"
    if "instr" in n:
        return "Instrumental"
    return name


def _guess_sections(chords: List[ChordEventModel], lyrics: List[LyricEventModel]) -> List[SectionModel]:
    if not chords:
        return []
    # naive: single section
    first = chords[0]
    return [SectionModel(kind="Verse", startSec=first.atSec, inferred=True)]


def to_timeline(raw_doc: Dict[str, Any], *, snap: float = 0.25) -> Tuple[SongTimeline, List[TimelineWarning], List[TimelineWarning]]:
    """Map analyzed doc (output of analyze_from_content/analyze_songdoc) to canonical SongTimeline.

    Returns (timeline, warnings, validation_warnings)
    warnings: non-fatal heuristics
    validation_warnings: structural issues (missing bpm, etc.)
    """
    warnings: List[TimelineWarning] = []
    validation: List[TimelineWarning] = []

    meta = raw_doc.get("metadata", {}) or {}
    # Accept multiple bpm field variants: bpm, tempo inside metadata, or top-level tempo
    bpm_val = (
        raw_doc.get("bpm")
        or meta.get("bpm")
        or meta.get("tempo")
        or raw_doc.get("tempo")
    )
    try:
        bpm = float(bpm_val) if bpm_val is not None else DEFAULT_BPM
    except Exception:
        bpm = DEFAULT_BPM
    if not isfinite(bpm) or bpm <= 0:
        bpm = DEFAULT_BPM
        validation.append(TimelineWarning(code="bpm.invalid", message="Invalid BPM, defaulted to 120"))
    ts = (
        raw_doc.get("timeSignature")
        or meta.get("time_signature")
        or raw_doc.get("time_signature")
        or meta.get("ts")
        or "4/4"
    )
    try:
        num_s, den_s = str(ts).split("/", 1)
        num = int(num_s) or 4
        den = int(den_s) or 4
    except Exception:
        num, den = DEFAULT_SIG
        validation.append(TimelineWarning(code="timesig.invalid", message="Invalid time signature, defaulted to 4/4"))

    tempo_map = [TempoMark(atSec=0.0, bpm=bpm)]
    time_sig_map = [TimeSigMark(atSec=0.0, num=num, den=den)]

    # Sections (analyzed doc provides sections with startBeat/lengthBeats OR startBeat only OR startSec)
    sections_in = raw_doc.get("sections") or []
    sections: List[SectionModel] = []
    # Collect chords that may be nested inside section definitions (JCRD style)
    nested_section_chords: List[Dict[str, Any]] = []
    for s in sections_in:
        # Support both analyzed-format (startBeat/startSec) and JCRD (start_time/end_time)
        start_beat = s.get("startBeat")
        start_sec = s.get("startSec")
        if start_beat is not None:
            start_sec = _beats_to_sec(float(start_beat), bpm)
        if start_sec is None and s.get("start_time") is not None:
            start_sec = float(s.get("start_time"))
        end_sec = None
        if s.get("endSec") is not None:
            end_sec = float(s.get("endSec"))
        elif s.get("end_time") is not None:
            end_sec = float(s.get("end_time"))
        else:
            lb = s.get("lengthBeats")
            if lb is not None and start_beat is not None:
                end_sec = _beats_to_sec(float(start_beat) + float(lb), bpm)
        orig_name = s.get("name")
        norm_kind = _normalize_section_kind(orig_name)
        sections.append(
            SectionModel(
                kind=norm_kind,
                startSec=float(start_sec or 0.0),
                endSec=end_sec,
                name=orig_name or norm_kind,
            )
        )
        # Extract nested chords
        if isinstance(s.get("chords"), list):
            for c in s.get("chords"):
                if c and (c.get("chord") or c.get("symbol") or c.get("name")):
                    # Annotate with section boundary for potential duration inference
                    if end_sec is not None:
                        c.setdefault("_section_end_sec", end_sec)
                    nested_section_chords.append(c)

    # Chords
    chord_rows = raw_doc.get("chords") or []
    # If no top-level chords, attempt chord_progression (JCRD) then nested section chords
    if not chord_rows:
        # Prefer explicit chord list fallback order
        if isinstance(raw_doc.get("chord_progression"), list):
            chord_rows = raw_doc.get("chord_progression")
        elif nested_section_chords:
            chord_rows = nested_section_chords
    else:
        # If we already have some chords but also a chord_progression, merge any that are not duplicates (by start/time symbol)
        cp = raw_doc.get("chord_progression")
        if isinstance(cp, list):
            chord_rows.extend(cp)
    # Also merge nested section chords if we didn't already collect them (avoid duplicates)
    if nested_section_chords and chord_rows is not nested_section_chords:
        chord_rows.extend(nested_section_chords)
    chords: List[ChordEventModel] = []
    for c in chord_rows:
        if not c:
            continue
        symbol = c.get("symbol") or c.get("name") or c.get("chord")
        if not symbol:
            continue
        if "startBeat" in c:
            at_beat_raw = float(c.get("startBeat") or 0.0)
        else:
            # Support multiple second-based start fields: start_sec, start_time (JCRD), time, startTime
            at_beat_raw = _sec_to_beats(
                float(
                    c.get("start_sec")
                    or c.get("start_time")
                    or c.get("time")
                    or c.get("startTime")
                    or 0.0
                ),
                bpm,
            )
        at_beat = _quantize(at_beat_raw, snap)
        at_sec = _beats_to_sec(at_beat, bpm)
        dur_beats = None
        if c.get("lengthBeats") is not None:
            dur_beats = float(c.get("lengthBeats"))
        elif c.get("durationBeats") is not None:
            dur_beats = float(c.get("durationBeats"))
        else:
            # JCRD style explicit end_time / duration or chord_progression duration
            if c.get("end_time") is not None and (
                c.get("start_time") is not None or c.get("time") is not None
            ):
                st_sec = float(c.get("start_time") or c.get("time"))
                et_sec = float(c.get("end_time"))
                dur_beats = _sec_to_beats(max(0.0, et_sec - st_sec), bpm)
            elif c.get("duration") is not None:
                # chord_progression structure
                dur_beats = _sec_to_beats(float(c.get("duration")), bpm)
            elif c.get("duration_sec") is not None:
                dur_beats = _sec_to_beats(float(c.get("duration_sec")), bpm)
        chords.append(ChordEventModel(symbol=symbol, atSec=at_sec, atBeat=at_beat, durationBeats=dur_beats))

    chords.sort(key=lambda ch: ch.atBeat)
    # Infer missing durations from next chord or section boundaries
    for i, ch in enumerate(chords):
        if ch.durationBeats is not None:
            continue
        next_ch = chords[i + 1] if i + 1 < len(chords) else None
        if next_ch:
            ch.durationBeats = max(0.25, next_ch.atBeat - ch.atBeat)
        else:
            # Use section end if inside a section
            for sec in sections:
                if ch.atSec >= sec.startSec and (sec.endSec is not None) and ch.atSec < sec.endSec:
                    sec_end_beat = _sec_to_beats(sec.endSec, bpm)
                    ch.durationBeats = max(0.25, sec_end_beat - ch.atBeat)
                    break

    # Lyrics
    lyric_rows = raw_doc.get("lyrics") or []
    # Accept multiple shapes:
    # - list of { text, ts_sec|timeSec|beat }
    # - dict { lines: [...] }
    # - list[str]
    if isinstance(lyric_rows, dict):
        lyric_rows = lyric_rows.get("lines") or []
    # Normalize string entries
    if isinstance(lyric_rows, list):
        lyric_rows = [
            ({"text": l} if isinstance(l, str) else l)
            for l in lyric_rows
            if l is not None
        ]
    lyrics: List[LyricEventModel] = []
    for idx, l in enumerate(lyric_rows):
        if not isinstance(l, dict):
            continue
        text = l.get("text")
        if not text:
            continue
        if "beat" in l and l.get("beat") is not None:
            at_beat_raw = float(l.get("beat") or 0.0)
        else:
            at_beat_raw = _sec_to_beats(float(l.get("timeSec") or l.get("ts_sec") or 0.0), bpm)
        at_beat = _quantize(at_beat_raw, snap)
        at_sec = _beats_to_sec(at_beat, bpm)
        lyr_id = l.get("id") or ("b" + str(at_beat))
        lyrics.append(LyricEventModel(id=str(lyr_id), atSec=at_sec, atBeat=at_beat, text=text))

    if not sections:
        sections = _guess_sections(chords, lyrics)
        if sections:
            warnings.append(TimelineWarning(code="sections.inferred", message="Sections inferred heuristically"))

    # Hover pairing: chord -> nearest lyric within 1 beat
    lyric_sorted = sorted(lyrics, key=lambda l: l.atBeat)
    for ch in chords:
        best = None
        best_dist = 1e9
        for ly in lyric_sorted:
            d = abs(ly.atBeat - ch.atBeat)
            if d < best_dist:
                best_dist = d
                best = ly
            if ly.atBeat > ch.atBeat + 1:
                break
        if best and best_dist <= 1:
            ch.lyricId = best.id

    # Structural validation
    if not chords:
        validation.append(TimelineWarning(code="chords.empty", message="No chords present"))
    if not lyrics:
        validation.append(TimelineWarning(code="lyrics.empty", message="No lyrics present"))
    if bpm <= 0:
        validation.append(TimelineWarning(code="bpm.missing", message="Missing BPM"))
    if num <= 0 or den <= 0:
        validation.append(TimelineWarning(code="timesig.missing", message="Missing time signature"))

    # Key / mode extraction (support metadata.key of form "Key E" or "E Major")
    key_val = raw_doc.get("key") or meta.get("key")
    mode_val = raw_doc.get("mode") or meta.get("mode")
    if key_val and isinstance(key_val, str):
        # Heuristic: last token that looks like pitch (A-G with optional #/b)
        parts = key_val.replace("_", " ").split()
        for tok in reversed(parts):
            t = tok.strip().upper()
            if t and t[0] in "ABCDEFG":
                key_val = tok.replace("Key", "").strip()
                break

    timeline = SongTimeline(
        id=str(raw_doc.get("id") or raw_doc.get("songId") or "unknown"),
        title=raw_doc.get("title"),
        artist=raw_doc.get("artist"),
        bpmDefault=bpm,
        timeSigDefault={"num": num, "den": den},
        tempoMap=tempo_map,
        timeSigMap=time_sig_map,
        sections=sections,
        chords=chords,
        lyrics=lyrics,
        key=key_val,
        mode=mode_val,
    )
    return timeline, warnings, validation
