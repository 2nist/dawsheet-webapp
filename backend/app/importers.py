from __future__ import annotations

import json
import os
from typing import List, Dict, Tuple


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
            if "songs" in obj and isinstance(obj["songs"], list):
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
