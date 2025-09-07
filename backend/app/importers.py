from __future__ import annotations

import json
import os
from typing import List, Dict, Tuple, Any

try:
    from .utils.tempo import convert_jcrd as _convert_jcrd
except Exception:  # pragma: no cover - fallback for import contexts
    _convert_jcrd = None  # type: ignore


def _decode_bytes(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


def import_json_file(filename: str, data: bytes) -> Tuple[List[Dict[str, str]], List[str]]:
    text = _decode_bytes(data)
    warnings: List[str] = []
    songs: List[Dict[str, str]] = []
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            # Special case: JCRD chord JSON with timing and tempo -> convert to beats/bars
            if _looks_like_jcrd(obj) and _convert_jcrd:
                converted = _convert_jcrd(obj)
                songs.extend(_render_converted_jcrd(filename, converted, warnings))
            elif "songs" in obj and isinstance(obj["songs"], list):
                for s in obj["songs"]:
                    songs.extend(_normalize_song_obj(s, warnings))
            else:
                songs.extend(_normalize_song_obj(obj, warnings))
        elif isinstance(obj, list):
            for s in obj:
                songs.extend(_normalize_song_obj(s, warnings))
        else:
            warnings.append(f"{filename}: JSON root must be object or array")
    except Exception as e:
        warnings.append(f"{filename}: JSON parse error: {e}")
    return songs, warnings


def _looks_like_jcrd(obj: Dict[str, Any]) -> bool:
    meta = obj.get("metadata") or {}
    if not isinstance(meta, dict):
        return False
    tempo = meta.get("tempo") or meta.get("bpm")
    has_timing = bool(obj.get("sections")) or bool(obj.get("chord_progression"))
    return (tempo is not None) and has_timing


def _render_converted_jcrd(filename: str, conv: Dict[str, Any], warnings: List[str]) -> List[Dict[str, str]]:
    """Render converted JCRD object to a Song dict with human-readable content."""
    meta = conv.get("metadata") or {}
    title = str(meta.get("title") or meta.get("name") or "Untitled").strip()
    artist = str(meta.get("artist") or "").strip()
    header = [
        f"Title: {title}",
        f"Artist: {artist}",
        f"Time: {meta.get('time_signature', '4/4')}  BPM: {meta.get('bpm')}  qBPM: {meta.get('qbpm')}  qBeats/Bar: {meta.get('quarter_beats_per_bar')}",
        "",
    ]

    lines: List[str] = []
    sections = conv.get("sections") or []
    if isinstance(sections, list) and sections:
        for sec in sections:
            name = sec.get("name") or "section"
            lines.append(f"[{name}]")
            for ch in sec.get("chords", []) or []:
                lines.append(
                    f"{ch.get('chord')}  @ bar {ch.get('start_bar')} beat {ch.get('start_beat_in_bar')}  "
                    f"for {ch.get('duration_bars')} bars ({ch.get('duration_qbeats')} qbeats)"
                )
            lines.append("")

    prog = conv.get("chord_progression") or []
    if isinstance(prog, list) and prog:
        lines.append("[progression]")
        for it in prog:
            lines.append(
                f"{it.get('chord')}  @ bar {it.get('start_bar')} beat {it.get('start_beat_in_bar')}  "
                f"for {it.get('duration_bars')} bars ({it.get('duration_qbeats')} qbeats)"
            )
        lines.append("")

    content = "\n".join(header + lines).strip()
    if not content:
        content = f"Converted from {filename}"
    return [{"title": title or "Untitled", "artist": artist, "content": content}]


def _normalize_song_obj(o: dict, warnings: List[str]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    if not isinstance(o, dict):
        warnings.append("Skipping non-object item in JSON array")
        return out
    title = str(o.get("title") or o.get("name") or "Untitled").strip()
    artist = str(o.get("artist") or o.get("composer") or "").strip()
    content = str(o.get("content") or o.get("lyrics") or "").strip()
    if not content and "sections" in o and isinstance(o["sections"], list):
        # Join section lines if provided
        content_lines: List[str] = []
        for sec in o["sections"]:
            name = str(sec.get("name") or "").strip()
            if name:
                content_lines.append(f"[{name}]")
            for ln in sec.get("lines", []) or []:
                txt = ln.get("text") if isinstance(ln, dict) else ln
                if txt:
                    content_lines.append(str(txt))
            content_lines.append("")
        content = "\n".join(content_lines).strip()
    out.append({"title": title, "artist": artist, "content": content})
    return out


def import_midi_file(filename: str, data: bytes) -> Tuple[List[Dict[str, str]], List[str]]:
    warnings: List[str] = []
    songs: List[Dict[str, str]] = []
    try:
        import mido  # type: ignore
        from io import BytesIO

        f = BytesIO(data)
        mid = mido.MidiFile(file=f)
        title = os.path.splitext(os.path.basename(filename))[0]
        track_names = []
        markers = []
        lyrics = []
        for track in mid.tracks:
            for msg in track:
                if msg.type == "track_name":
                    track_names.append(str(msg.name))
                elif msg.type == "marker":
                    markers.append(str(getattr(msg, "text", "")))
                elif msg.type == "lyrics":
                    lyrics.append(str(getattr(msg, "text", "")))
        content_parts = []
        if track_names:
            content_parts.append("[Tracks]\n" + "\n".join(track_names))
        if markers:
            content_parts.append("[Markers]\n" + "\n".join(markers))
        if lyrics:
            content_parts.append("[Lyrics]\n" + "\n".join(lyrics))
        if not content_parts:
            content_parts.append("Instrumental")
        content = "\n\n".join(content_parts)
        songs.append({"title": title, "artist": "", "content": content})
    except Exception as e:
        warnings.append(f"{filename}: MIDI parse error: {e}")
    return songs, warnings


def import_mp3_file(filename: str, data: bytes) -> Tuple[List[Dict[str, str]], List[str]]:
    warnings: List[str] = []
    songs: List[Dict[str, str]] = []
    try:
        from io import BytesIO
        from mutagen import File as MutagenFile  # type: ignore
        bio = BytesIO(data)
        mf = MutagenFile(bio, easy=True)
        title = ""
        artist = ""
        if mf is not None:
            title = (mf.get("title", [""]) or [""])[0]
            artist = (mf.get("artist", [""]) or [""])[0]
        if not title:
            title = os.path.splitext(os.path.basename(filename))[0]
        content = ""  # Could be extended to read USLT (lyrics) frames with ID3-specific API
        songs.append({"title": str(title), "artist": str(artist), "content": content})
    except Exception as e:
        warnings.append(f"{filename}: MP3 parse error: {e}")
    return songs, warnings
