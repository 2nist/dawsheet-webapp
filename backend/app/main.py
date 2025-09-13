"""
Simplified Docker-Compatible FastAPI Server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Try to import LRCLIB service
try:
    from .services.lyrics_providers.lrclib import search_timestamped_lyrics
    LYRICS_ENABLED = True
except ImportError:
    LYRICS_ENABLED = False
    search_timestamped_lyrics = None

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

    # Parse content if it's a JSON string (like Beatles files) or use song data directly
    parsed_content = {}
    if song.get("content"):
        try:
            import json
            parsed_content = json.loads(song["content"])
        except:
            pass
    else:
        # For Beatles data imported via enhanced POST endpoint, use song directly
        parsed_content = song

    # Convert to doc format (what the frontend expects)
    doc = {
        "title": song.get("title", "Untitled"),
        "artist": song.get("artist", "Unknown Artist"),
        "bpm": parsed_content.get("metadata", {}).get("tempo", 120),  # Use tempo from Beatles files
        "timeSignature": parsed_content.get("metadata", {}).get("time_signature", "4/4"),  # Use time sig from Beatles files
        "sections": [],
        "chords": [],
        "lyrics": [],
        "issues": []
    }

    # Clean the title if it has track numbers or underscores
    if doc["title"]:
        # Import title cleaning utilities
        from .utils.lyrics import clean_title_for_lyrics, normalize_artist_name
        doc["title"] = clean_title_for_lyrics(doc["title"])
        doc["artist"] = normalize_artist_name(doc["artist"])

    # Convert Beatles sections format
    if parsed_content.get("sections"):
        for i, section in enumerate(parsed_content["sections"]):
            doc["sections"].append({
                "id": f"section_{i}",
                "name": section.get("name", "Section"),
                "startBeat": section.get("start_time", 0) * 2,  # Convert seconds to beats (rough conversion)
                "lengthBeats": (section.get("end_time", 0) - section.get("start_time", 0)) * 2
            })

    # Fallback for legacy structure format
    elif song.get("structure"):
        for i, section in enumerate(song["structure"]):
            doc["sections"].append({
                "id": f"section_{i}",
                "name": section.get("label", section.get("section", "Section")),
                "startBeat": section.get("time", 0) * 2,
                "lengthBeats": 8
            })

    # Convert Beatles chord progression format
    if parsed_content.get("chord_progression"):
        for i, chord in enumerate(parsed_content["chord_progression"]):
            doc["chords"].append({
                "symbol": chord.get("chord", "C"),
                "startBeat": chord.get("time", 0) * 2  # Convert seconds to beats
            })

    # Fallback for legacy chords format
    elif song.get("chords"):
        for i, chord in enumerate(song["chords"]):
            doc["chords"].append({
                "symbol": chord.get("chord", "C"),
                "startBeat": chord.get("time", 0) * 2
            })

    # Convert lyrics - handle both LRCLIB format and legacy format
    if song.get("lyrics"):
        lyrics_data = song["lyrics"]

        # Check if it's LRCLIB format with 'lines' array
        if isinstance(lyrics_data, dict) and lyrics_data.get("lines"):
            for line in lyrics_data["lines"]:
                if isinstance(line, dict) and line.get("text"):
                    doc["lyrics"].append({
                        "text": line["text"],
                        "ts_sec": line.get("ts_sec"),
                        "beat": line.get("ts_sec", 0) * 2 if line.get("ts_sec") is not None else None
                    })

        # Legacy format with 'verses'
        elif isinstance(lyrics_data, dict) and lyrics_data.get("verses"):
            for i, verse in enumerate(lyrics_data["verses"]):
                doc["lyrics"].append({
                    "text": verse.get("text", ""),
                    "beat": verse.get("time", 0) * 2,
                    "ts_sec": verse.get("time", 0)
                })

    return doc

@app.post("/songs")
async def create_song(song: dict):
    """Enhanced song creation with automatic LRCLIB lyrics fetching for .jcrd.json files"""

    # Check if this is a Beatles .jcrd.json file with metadata
    if "metadata" in song and song["metadata"].get("title") and song["metadata"].get("artist"):
        # Extract clean title and artist from Beatles metadata
        from .utils.lyrics import clean_title_for_lyrics, normalize_artist_name
        clean_title = clean_title_for_lyrics(song["metadata"]["title"])
        clean_artist = normalize_artist_name(song["metadata"]["artist"])

        # Create new song with cleaned metadata
        new_song = {
            "id": str(len(songs) + 1),
            "title": clean_title,
            "artist": clean_artist,
            **song
        }

        # Automatically fetch LRCLIB lyrics if available
        if LYRICS_ENABLED and search_timestamped_lyrics:
            try:
                print(f"Fetching LRCLIB lyrics for: '{clean_title}' by '{clean_artist}'")
                lyrics_result = await search_timestamped_lyrics(
                    title=clean_title,
                    artist=clean_artist
                )
                if lyrics_result.get("matched") and lyrics_result.get("lines"):
                    new_song["lyrics"] = lyrics_result
                    new_song["metadata"] = new_song.get("metadata", {})
                    new_song["metadata"]["lyrics_source"] = "lrclib_auto"
                    print(f"Successfully fetched {len(lyrics_result['lines'])} lyric lines from LRCLIB")
                else:
                    print("No matching lyrics found in LRCLIB")
            except Exception as e:
                print(f"Error fetching LRCLIB lyrics: {e}")
                # Continue without lyrics
    else:
        # Standard song creation
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

    # Lyrics fetching is disabled for now - would need async support
    new_song["metadata"]["lyrics_source"] = "disabled"

    songs.append(new_song)
    return {"success": True, "song_id": new_song["id"], "message": f"Imported '{title}' by {artist}"}

@app.post("/api/v1/import/isophonics")
def import_isophonics(data: dict):
    """Dedicated Isophonics import endpoint"""
    return import_json(data)

@app.post("/songs/{song_id}/lyrics")
async def fetch_lyrics_for_song(song_id: str):
    """Fetch lyrics for an existing song"""
    if not LYRICS_ENABLED or not search_timestamped_lyrics:
        return {"error": "Lyrics service not available"}

    # Find the song
    song = None
    for s in songs:
        if s["id"] == song_id:
            song = s
            break

    if not song:
        return {"error": "Song not found"}

    try:
        # Import title cleaning utility
        from app.utils.lyrics import clean_title_for_lyrics, normalize_artist_name

        # Clean the title and artist for better matching
        clean_title = clean_title_for_lyrics(song["title"])
        clean_artist = normalize_artist_name(song["artist"])

        fetched_lyrics = await search_timestamped_lyrics(
            title=clean_title,
            artist=clean_artist,
            album=song.get("album", "")
        )
        if fetched_lyrics.get("matched"):
            song["lyrics"] = fetched_lyrics
            song["metadata"]["lyrics_source"] = "lrclib"
            return {"success": True, "lyrics": fetched_lyrics, "clean_title_used": clean_title}
        else:
            return {"success": False, "message": "No lyrics found", "clean_title_used": clean_title}
    except Exception as e:
        return {"error": f"Failed to fetch lyrics: {e}"}

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

# Include lyrics search router
try:
    from .routers.lyrics_search import router as lyrics_router
    app.include_router(lyrics_router, prefix="/v1/lyrics")
except ImportError:
    # Lyrics search not available
    @app.get("/v1/lyrics/search")
    def lyrics_search_fallback():
        return {"error": "Lyrics search not available"}

# Include unified import system
try:
    from .import_system.router import router as unified_import_router
    app.include_router(unified_import_router)
except ImportError:
    # Unified import system not available
    @app.get("/import/formats")
    def import_formats_fallback():
        return {"error": "Unified import system not available"}

    @app.post("/import/unified")
    def import_unified_fallback():
        return {"error": "Unified import system not available"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
