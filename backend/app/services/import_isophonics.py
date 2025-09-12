from typing import Dict, Any, List, Optional
from ..models.song import Song, SongMetadata, Section, Lane, ChordItem, LyricItem
import uuid

def from_isophonics(data: Dict[str, Any]) -> Song:
    """
    Convert Isophonics format JSON to our Song model.

    Expected Isophonics format:
    {
        "title": "Song Title",
        "artist": "Artist Name",
        "metadata": {
            "key": "C",
            "tempo": 120,
            "time_signature": "4/4"
        },
        "sections": [
            {"name": "Verse", "start": 0, "end": 32},
            {"name": "Chorus", "start": 32, "end": 64}
        ],
        "chord_progression": [
            {"beat": 0, "chord": "C", "duration": 4},
            {"beat": 4, "chord": "Am", "duration": 4}
        ],
        "lyrics": [
            {"beat": 0, "text": "Hello", "duration": 1},
            {"beat": 1, "text": "world", "duration": 1}
        ]
    }
    """

    # Extract basic song info
    title = data.get("title", "Imported Song")
    artist = data.get("artist", "Unknown Artist")
    content = str(data)  # Store original JSON as content

    # Extract and normalize metadata
    meta_data = data.get("metadata", {})
    metadata = SongMetadata(
        key=meta_data.get("key", "C"),
        tempo=meta_data.get("tempo", 120),
        time_signature=meta_data.get("time_signature", "4/4"),
        genre=meta_data.get("genre"),
        year=meta_data.get("year")
    )

    # Convert sections
    sections = []
    section_data = data.get("sections", [])
    for i, section in enumerate(section_data):
        sections.append(Section(
            id=str(uuid.uuid4()),
            name=section.get("name", f"Section {i+1}"),
            start_beat=float(section.get("start", 0)),
            length_beats=float(section.get("end", 32) - section.get("start", 0)),
            color=_get_section_color(i)
        ))

    # Convert chord progression to chord lane
    lanes = []
    chord_progression = data.get("chord_progression", [])
    if chord_progression:
        chord_items = []
        for chord_data in chord_progression:
            chord_items.append({
                "id": str(uuid.uuid4()),
                "beat": float(chord_data.get("beat", 0)),
                "symbol": chord_data.get("chord", "C"),
                "duration": float(chord_data.get("duration", 4))
            })

        lanes.append(Lane(
            id=str(uuid.uuid4()),
            type="chords",
            name="Chords",
            items=chord_items
        ))

    # Convert lyrics to lyrics lane
    lyrics_data = data.get("lyrics", [])
    if lyrics_data:
        lyric_items = []
        for lyric in lyrics_data:
            lyric_items.append({
                "id": str(uuid.uuid4()),
                "beat": float(lyric.get("beat", 0)),
                "text": lyric.get("text", ""),
                "duration": float(lyric.get("duration", 1))
            })

        lanes.append(Lane(
            id=str(uuid.uuid4()),
            type="lyrics",
            name="Lyrics",
            items=lyric_items
        ))

    return Song(
        title=title,
        artist=artist,
        content=content,
        metadata=metadata,
        sections=sections,
        lanes=lanes
    )

def _get_section_color(index: int) -> str:
    """Get a color for a section based on its index"""
    colors = [
        "#8B5CF6",  # Purple
        "#10B981",  # Green
        "#F59E0B",  # Yellow
        "#EF4444",  # Red
        "#3B82F6",  # Blue
        "#6B7280",  # Gray
        "#F97316",  # Orange
        "#8B5A2B"   # Brown
    ]
    return colors[index % len(colors)]

def normalize_isophonics_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize and validate Isophonics data before conversion.
    Handles various formats and missing fields.
    """
    normalized = {
        "title": data.get("title", data.get("name", "Imported Song")),
        "artist": data.get("artist", data.get("performer", "Unknown Artist")),
        "metadata": {},
        "sections": [],
        "chord_progression": [],
        "lyrics": []
    }

    # Normalize metadata
    if "metadata" in data:
        meta = data["metadata"]
        normalized["metadata"] = {
            "key": meta.get("key", meta.get("tonic", "C")),
            "tempo": meta.get("tempo", meta.get("bpm", 120)),
            "time_signature": meta.get("time_signature", meta.get("meter", "4/4"))
        }

    # Normalize sections
    if "sections" in data:
        for section in data["sections"]:
            normalized["sections"].append({
                "name": section.get("name", section.get("label", "Section")),
                "start": section.get("start", section.get("start_time", 0)),
                "end": section.get("end", section.get("end_time", 32))
            })

    # Normalize chord progression
    if "chord_progression" in data:
        for chord in data["chord_progression"]:
            normalized["chord_progression"].append({
                "beat": chord.get("beat", chord.get("time", 0)),
                "chord": chord.get("chord", chord.get("symbol", "C")),
                "duration": chord.get("duration", chord.get("length", 4))
            })
    elif "chords" in data:  # Alternative format
        for chord in data["chords"]:
            normalized["chord_progression"].append({
                "beat": chord.get("beat", chord.get("time", 0)),
                "chord": chord.get("chord", chord.get("symbol", "C")),
                "duration": chord.get("duration", chord.get("length", 4))
            })

    # Normalize lyrics
    if "lyrics" in data:
        for lyric in data["lyrics"]:
            normalized["lyrics"].append({
                "beat": lyric.get("beat", lyric.get("time", 0)),
                "text": lyric.get("text", lyric.get("word", "")),
                "duration": lyric.get("duration", lyric.get("length", 1))
            })

    return normalized
