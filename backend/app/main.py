"""
Simplified Docker-Compatible FastAPI Server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DAWSheet Docker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage
songs = [
    {"id": "1", "title": "Demo Song 1", "artist": "Demo Artist"},
    {"id": "2", "title": "Demo Song 2", "artist": "Another Artist"},
]

@app.get("/")
def root():
    return {"message": "DAWSheet Docker API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/health")
def api_health():
    return {"status": "healthy"}

@app.get("/songs")
def get_songs():
    return songs

@app.get("/api/v1/songs")
def get_songs_v1():
    return songs

@app.get("/songs/{song_id}")
def get_song(song_id: str):
    """Get detailed song information"""
    for song in songs:
        if song["id"] == song_id:
            return song
    return {"error": "Song not found"}, 404

@app.get("/v1/songs/{song_id}/timeline")
def get_song_timeline(song_id: str):
    """Get song in timeline format for frontend compatibility"""
    # Find the song
    song = None
    for s in songs:
        if s["id"] == song_id:
            song = s
            break

    if not song:
        return {"error": "Song not found"}, 404

    # Convert to timeline format
    timeline = {
        "title": song.get("title", "Untitled"),
        "artist": song.get("artist", "Unknown Artist"),
        "bpmDefault": 120,  # Default BPM
        "timeSigDefault": {"num": 4, "den": 4},  # Default time signature
        "sections": [],
        "chords": [],
        "lyrics": []
    }

    # Convert sections
    if song.get("structure"):
        for i, section in enumerate(song["structure"]):
            timeline["sections"].append({
                "id": f"section_{i}",
                "name": section.get("label", section.get("section", "Section")),
                "startBeat": section.get("time", 0) * 2,  # Convert time to beats (assuming 2 beats per second)
                "lengthBeats": 8,  # Default section length
                "color": "#e0e7ff"  # Default color
            })

    # Convert chords
    if song.get("chords"):
        for i, chord in enumerate(song["chords"]):
            timeline["chords"].append({
                "id": f"chord_{i}",
                "symbol": chord.get("chord", "C"),
                "startBeat": chord.get("time", 0) * 2,  # Convert time to beats
                "lengthBeats": 2  # Default chord length
            })

    # Convert lyrics
    if song.get("lyrics") and song["lyrics"].get("verses"):
        for i, verse in enumerate(song["lyrics"]["verses"]):
            timeline["lyrics"].append({
                "id": f"lyric_{i}",
                "text": verse.get("text", ""),
                "beat": verse.get("time", 0) * 2,  # Convert time to beats
                "row": i
            })

    return {
        "timeline": timeline,
        "warnings": []
    }

@app.get("/v1/songs/{song_id}/doc")
def get_song_doc(song_id: str):
    """Get song in doc format for frontend compatibility"""
    # Find the song
    song = None
    for s in songs:
        if s["id"] == song_id:
            song = s
            break

    if not song:
        return {"error": "Song not found"}, 404

    # Convert to doc format (what the frontend expects)
    doc = {
        "title": song.get("title", "Untitled"),
        "artist": song.get("artist", "Unknown Artist"),
        "bpm": 120,  # Default BPM
        "timeSignature": "4/4",  # Default time signature
        "sections": [],
        "chords": [],
        "lyrics": [],
        "issues": []
    }

    # Convert sections
    if song.get("structure"):
        for i, section in enumerate(song["structure"]):
            doc["sections"].append({
                "id": f"section_{i}",
                "name": section.get("label", section.get("section", "Section")),
                "startBeat": section.get("time", 0) * 2,  # Convert time to beats (assuming 2 beats per second)
                "lengthBeats": 8  # Default section length
            })

    # Convert chords
    if song.get("chords"):
        for i, chord in enumerate(song["chords"]):
            doc["chords"].append({
                "symbol": chord.get("chord", "C"),
                "startBeat": chord.get("time", 0) * 2  # Convert time to beats
            })

    # Convert lyrics
    if song.get("lyrics") and song["lyrics"].get("verses"):
        for i, verse in enumerate(song["lyrics"]["verses"]):
            doc["lyrics"].append({
                "text": verse.get("text", ""),
                "beat": verse.get("time", 0) * 2,  # Convert time to beats
                "ts_sec": verse.get("time", 0)
            })

    return doc

@app.post("/songs")
def create_song(song: dict):
    new_song = {"id": str(len(songs) + 1), **song}
    songs.append(new_song)
    return new_song

@app.post("/import/json")
def import_json(data: dict):
    """Enhanced import with full Isophonics format support"""
    # Extract metadata
    metadata = data.get("metadata", {})
    title = metadata.get("title", data.get("title", "Imported Song"))
    artist = metadata.get("artist", data.get("artist", "Unknown Artist"))
    album = metadata.get("album", data.get("album", ""))
    year = metadata.get("year", data.get("year", ""))
    duration = metadata.get("duration", data.get("duration", 0))

    # Extract musical data with fallbacks for different formats
    chords = data.get("chords", data.get("chord_progression", []))
    lyrics = data.get("lyrics", {})
    structure = data.get("structure", data.get("sections", []))

    # Normalize chord format if needed
    if chords and isinstance(chords, list) and len(chords) > 0:
        if isinstance(chords[0], dict) and "chord" in chords[0]:
            # Already in correct format
            pass
        elif isinstance(chords[0], dict) and "time" in chords[0]:
            # Convert time-based format
            normalized_chords = []
            for chord_data in chords:
                normalized_chords.append({
                    "time": chord_data.get("time", 0),
                    "chord": chord_data.get("chord", chord_data.get("symbol", "C"))
                })
            chords = normalized_chords

    # Normalize structure format if needed
    if structure and isinstance(structure, list) and len(structure) > 0:
        if isinstance(structure[0], dict) and "section" in structure[0]:
            # Already in correct format
            pass
        elif isinstance(structure[0], dict) and "name" in structure[0]:
            # Convert name-based format
            normalized_structure = []
            for section in structure:
                normalized_structure.append({
                    "time": section.get("start", section.get("time", 0)),
                    "section": section.get("name", "section").lower(),
                    "label": section.get("name", "Section")
                })
            structure = normalized_structure

    # Create rich song object
    new_song = {
        "id": str(len(songs) + 1),
        "title": title,
        "artist": artist,
        "album": album,
        "year": year,
        "duration": duration,
        "chords": chords,
        "lyrics": lyrics,
        "structure": structure,
        "metadata": {
            "imported": True,
            "format": "isophonics",
            "chord_count": len(chords),
            "structure_sections": len(structure)
        }
    }

    songs.append(new_song)
    return {"success": True, "song_id": new_song["id"], "message": f"Imported '{title}' by {artist}"}

@app.post("/api/v1/import/isophonics")
def import_isophonics(data: dict):
    """Dedicated Isophonics import endpoint"""
    return import_json(data)

@app.post("/parse")
def parse_text(data: dict):
    """Text parsing endpoint for legacy compatibility"""
    text = data.get("text", "")
    lines = text.strip().split('\n')
    title = lines[0] if lines else "Text Import"

    new_song = {
        "id": str(len(songs) + 1),
        "title": title,
        "artist": "Text Import",
        "content": text,
        "metadata": {"imported": True, "format": "text"}
    }

    songs.append(new_song)
    return {"success": True, "song_id": new_song["id"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
