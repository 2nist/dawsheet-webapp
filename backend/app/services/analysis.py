from __future__ import annotations

from typing import Any, Dict, List, Tuple
import re

from ..utils.timeline import seconds_to_beats, beats_to_bars, quantize_beats, align_chords_to_grid


def analyze_songdoc(jcrd_like: Dict[str, Any]) -> Dict[str, Any]:
    meta = jcrd_like.get("metadata") or {}
    bpm = float(meta.get("tempo") or meta.get("bpm") or jcrd_like.get("bpm") or 120.0)
    time_sig = str(meta.get("time_signature") or jcrd_like.get("timeSignature") or "4/4")

    # Collect chords from chord_progression or sections
    chords: List[Dict[str, Any]] = []
    # direct chord list with startBeat (as in tests)
    for ch in jcrd_like.get("chords", []) or []:
        if not isinstance(ch, dict):
            continue
        if "startBeat" in ch:
            chords.append({"symbol": ch.get("name") or ch.get("symbol"), "startBeat": float(ch.get("startBeat", 0.0))})
        else:
            chords.append({"symbol": ch.get("name") or ch.get("symbol"), "start_sec": float(ch.get("start_sec") or ch.get("time") or 0.0)})
    # fallbacks
    if not chords:
        for it in jcrd_like.get("chord_progression", []) or []:
            if not isinstance(it, dict):
                continue
            chords.append({"symbol": it.get("chord"), "start_sec": float(it.get("time", 0.0))})
    if not chords:
        for sec in jcrd_like.get("sections", []) or []:
            for ch in sec.get("chords", []) or []:
                chords.append({"symbol": ch.get("chord"), "start_sec": float(ch.get("start_time", 0.0))})

    # Quantized chord beats
    chords_q_in = []
    for c in chords:
        if "startBeat" in c:
            chords_q_in.append({"symbol": c.get("symbol"), "startBeat": c.get("startBeat")})
        else:
            chords_q_in.append({"symbol": c.get("symbol"), "start_sec": c.get("start_sec")})
    chords_q = align_chords_to_grid(chords_q_in, bpm=bpm, time_sig=time_sig, grid="1/4")
    chords_q = [{"symbol": c.get("symbol"), "startBeat": c.get("startBeat")} for c in chords_q]

    # Lyrics from jcrd_like. If separate, caller can inject before calling this.
    lyrics = []
    lyr_in = jcrd_like.get("lyrics") or []
    if isinstance(lyr_in, dict):
        lyr_in = lyr_in.get("lines") or []
    for ln in lyr_in:
        if not isinstance(ln, dict):
            continue
        lyrics.append({"ts_sec": ln.get("ts_sec"), "text": ln.get("text")})

    # If lyrics are not found in structured jcrd_like, try parsing from content string
    if not lyrics and "content" in jcrd_like and isinstance(jcrd_like["content"], str):
        lyrics = _parse_lyrics_from_content(jcrd_like["content"])

    lyrics = []
    lyr_in = jcrd_like.get("lyrics") or []
    if isinstance(lyr_in, dict):
        lyr_in = lyr_in.get("lines") or []
    for ln in lyr_in:
        if not isinstance(ln, dict):
            continue
        lyrics.append({"ts_sec": ln.get("ts_sec"), "text": ln.get("text")})

    # If lyrics are not found in structured jcrd_like, try parsing from content string
    if not lyrics and "content" in jcrd_like and isinstance(jcrd_like["content"], str):
        lyrics = _parse_lyrics_from_content(jcrd_like["content"])

    # Sections from input file, or heuristic if not present
    sections: List[Dict[str, Any]] = []
    input_sections = jcrd_like.get("sections")
    if input_sections and isinstance(input_sections, list):
        first_musical_section_start_beat = 0.0
        # Find the start beat of the first non-silence section
        for sec in input_sections:
            if isinstance(sec, dict) and sec.get("name") != "silence":
                first_musical_section_start_beat = seconds_to_beats(float(sec.get("start_time", 0.0)), bpm)
                break

        for sec in input_sections:
            if not isinstance(sec, dict): continue
            start_time = float(sec.get("start_time", 0.0))
            end_time = float(sec.get("end_time", 0.0))
            sections.append({
                "name": sec.get("name", "section"),
                "startBeat": seconds_to_beats(start_time, bpm) - first_musical_section_start_beat,
                "lengthBeats": seconds_to_beats(end_time - start_time, bpm),
                "color": "#5B8DEF",  # TODO: color map for section names
            })
    elif chords_q:
        # fallback heuristic: new section every 32 beats (8 bars of 4/4), label alternates Verse/Chorus
        beats_per_section = 32 if time_sig.startswith("4/") else 24
        names = ["Verse", "Chorus"]
        start = 0.0
        i = 0
        # rough song length estimate from last chord
        end_guess = (chords_q[-1]["startBeat"] or 0.0) + 16
        while start < end_guess:
            sections.append({
                "name": names[i % len(names)],
                "startBeat": round(start, 3),
                "lengthBeats": beats_per_section,
                "color": "#5B8DEF" if (i % 2 == 0) else "#F59E0B",
            })
            i += 1
            start += beats_per_section

    # Issues
    issues: List[str] = []
    # Overlaps (chords with same startBeat)
    seen = {}
    for c in chords_q:
        sb = c.get("startBeat")
        if sb in seen:
            issues.append(f"overlapping chords at beat {sb}")
        seen[sb] = True

    # Output shape
    doc = {
        "title": meta.get("title") or jcrd_like.get("title"),
        "artist": meta.get("artist") or jcrd_like.get("artist"),
        "bpm": bpm,
        "timeSignature": time_sig,
        "sections": sections,
        "chords": chords_q,
        "lyrics": lyrics,
    }
    return {**doc, "issues": issues}


def analyze_from_content(title: str, artist: str, content: str, *, bpm: float = 120.0, time_sig: str = "4/4") -> Dict[str, Any]:
    """Heuristic analysis from saved content (No Reply-style).
    Assumptions: numeric group markers, chord lines above lyric lines, double-space between chords.
    """
    # Fast path: if content itself looks like a JCRD-style JSON blob, parse and passthrough to songdoc analyzer
    c_strip = (content or "").lstrip()
    if c_strip.startswith("{") and ("\"metadata\"" in c_strip or "\"chord_progression\"" in c_strip or "\"sections\"" in c_strip):
        import json
        try:
            obj = json.loads(content)
            if isinstance(obj, dict):
                return analyze_songdoc(obj)
        except Exception:
            # fall back to heuristic parsing
            pass
    chords: List[Dict[str, Any]] = []
    lyrics: List[Dict[str, Any]] = []
    current_bar = 1
    beats_per_bar = 4 if time_sig.startswith("4/") else 3
    beat_stride = beats_per_bar  # place each chord on new bar by default
    next_start_beat = 0.0
    # Chord token matcher (e.g., C, F#m7, Bbmaj7/G)
    chord_re = re.compile(r"^(?:N|[A-G](?:#|b)?(?:(?:maj|min|m|dim|aug|sus(?:2|4)?|add\d+|M7|maj7|m7|dim7|\+|°)?\d*(?:sus\d+)?)?(?:/[A-G](?:#|b)?)?)$")

    def parse_chord_line(s: str) -> List[str]:
        # Remove barlines and extra punctuation used for grids
        s_clean = s.replace("|", " ").replace("‖", " ").replace("·", " ").replace("—", " ")
        s_clean = re.sub(r"\s+", " ", s_clean.strip())
        if not s_clean:
            return []
        parts = [p for p in s_clean.split(" ") if p]
        # Consider it a chord line if all tokens look like chords and at least 1-2 tokens exist
        chord_like = [p for p in parts if chord_re.match(p)]
        if chord_like and len(chord_like) == len(parts):
            return chord_like
        # Fallback to double-space heuristic (legacy No Reply-style)
        if "  " in s and not s.startswith("["):
            parts2 = [p for p in s.split("  ") if p.strip()]
            chord_like2 = [p.strip() for p in parts2 if chord_re.match(p.strip())]
            if chord_like2 and len(chord_like2) == len(parts2):
                return chord_like2
        return []

    for raw in (content or "").splitlines():
        s = raw.strip()
        if not s:
            continue
        # group marker line
        if s.isdigit():
            try:
                current_bar = int(s)
                next_start_beat = (current_bar - 1) * beats_per_bar
                continue
            except Exception:
                pass
        # chord line detection (supports single- or multi-space separated tokens, with optional barlines)
        chord_tokens = parse_chord_line(s)
        if chord_tokens:
            for name in chord_tokens:
                chords.append({"symbol": name, "startBeat": round(next_start_beat, 3)})
                next_start_beat += beat_stride
            continue
        # else treat as lyric line
        lyrics.append({"ts_sec": None, "text": s})

    # Sections heuristic: blocks of N bars
    beats_per_section = 32 if time_sig.startswith("4/") else 24
    sections: List[Dict[str, Any]] = []
    if chords:
        names = ["Verse", "Chorus"]
        start = 0.0
        i = 0
        end_guess = (chords[-1]["startBeat"] or 0.0) + beats_per_section
        while start < end_guess:
            sections.append({
                "name": names[i % len(names)],
                "startBeat": round(start, 3),
                "lengthBeats": beats_per_section,
                "color": "#5B8DEF" if (i % 2 == 0) else "#F59E0B",
            })
            start += beats_per_section
            i += 1

    # Issues
    issues: List[str] = []
    seen = set()
    for c in chords:
        sb = c["startBeat"]
        if sb in seen:
            issues.append(f"overlapping chords at beat {sb}")
        seen.add(sb)

    doc = {
        "title": title,
        "artist": artist,
        "bpm": bpm,
        "timeSignature": time_sig,
        "sections": sections,
        "chords": chords,
        "lyrics": lyrics,
        "issues": issues,
    }
    return doc
