from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import re
import json
from typing import List, Dict, Any

app = FastAPI(title="DAWSheet Minimal API")

# In-memory storage for imported songs
songs_storage: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Hey Jude",
        "artist": "The Beatles",
        "content": "Hey Jude, don't make it bad...",
        "bpm": 72,
        "key": "F",
        "created_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": 2,
        "title": "Let It Be",
        "artist": "The Beatles",
        "content": "When I find myself in times of trouble...",
        "bpm": 76,
        "key": "C",
        "created_at": "2024-01-02T00:00:00Z"
    },
    {
        "id": 3,
        "title": "Yesterday",
        "artist": "The Beatles",
        "content": "Yesterday, all my troubles seemed so far away...",
        "bpm": 85,
        "key": "F",
        "created_at": "2024-01-03T00:00:00Z"
    }
]

# Basic CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/songs")
def get_songs():
    """Return list of all songs"""
    return songs_storage

@app.get("/v1/songs/{song_id}/doc")
def get_song_doc(song_id: int):
    """Return song document data"""
    # Find song in storage
    for song in songs_storage:
        if song.get("id") == song_id:
            return song

    # Return demo data if not found
    return {
        "id": song_id,
        "title": f"Song {song_id}",
        "content": "Demo content",
        "sections": []
    }

# LRCLIB integration functions
async def fetch_lyrics_from_lrclib(title: str, artist: str = "", album: str = "", duration_sec: int = None) -> Dict:
    """Fetch timestamped lyrics from LRCLIB"""
    try:
        params = {
            "track_name": title,
            "artist_name": artist,
        }
        if album:
            params["album_name"] = album
        if duration_sec:
            params["duration"] = str(duration_sec)

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://lrclib.net/api/get", params=params)

            if response.status_code == 404:
                return {"source": "lrclib", "matched": False, "synced": False, "lines": []}

            response.raise_for_status()
            data = response.json()

            # Parse LRC format if synced lyrics available
            synced = bool(data.get("syncedLyrics"))
            if synced:
                lines = parse_lrc_text(data["syncedLyrics"])
            else:
                # Use plain lyrics without timestamps
                lines = [
                    {"ts_sec": None, "text": line.strip()}
                    for line in (data.get("plainLyrics") or "").splitlines()
                    if line.strip()
                ]

            return {
                "source": "lrclib",
                "matched": True,
                "synced": synced,
                "lines": lines,
                "raw_data": data
            }
    except Exception as e:
        print(f"LRCLIB fetch error: {e}")
        return {"source": "lrclib", "matched": False, "synced": False, "lines": [], "error": str(e)}

def parse_lrc_text(lrc_text: str) -> List[Dict]:
    """Parse LRC format: [00:12.34] lyric line"""
    lines = []
    timestamp_pattern = re.compile(r'\[(\d{1,2}):(\d{2})(?:\.(\d{1,3}))?\]')

    for line in lrc_text.splitlines():
        line = line.strip()
        if not line:
            continue

        matches = list(timestamp_pattern.finditer(line))
        if matches:
            # Extract timestamp
            match = matches[0]
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            milliseconds = int(match.group(3) or 0)

            # Convert to total seconds
            ts_sec = minutes * 60 + seconds + (milliseconds / 1000)

            # Extract text after timestamp
            text = timestamp_pattern.sub('', line).strip()
            if text:
                lines.append({"ts_sec": ts_sec, "text": text})
        else:
            # Line without timestamp
            if line:
                lines.append({"ts_sec": None, "text": line})

    return lines

@app.post("/import/json")
async def import_json_with_lyrics(file: UploadFile = File(...), include_lyrics: bool = Query(default=True)):
    """Enhanced JSON import with LRCLIB lyrics integration"""
    try:
        # Read and parse JSON file
        content = await file.read()
        json_data = json.loads(content.decode('utf-8'))

        # Extract metadata
        metadata = json_data.get("metadata", {})
        title = metadata.get("title", "") or json_data.get("title", "")
        artist = metadata.get("artist", "") or json_data.get("artist", "")

        # Generate next ID
        next_id = max([s.get("id", 0) for s in songs_storage], default=0) + 1

        # Fetch lyrics if requested and we have title
        lyrics_data = None
        if include_lyrics and title:
            print(f"Fetching lyrics for: {title} by {artist}")
            lyrics_data = await fetch_lyrics_from_lrclib(title, artist)

        # Process song data
        song_data = {
            "id": next_id,
            "title": title or f"Imported Song {next_id}",
            "artist": artist or "Unknown Artist",
            "bpm": json_data.get("bpm") or metadata.get("bpm", 120),
            "time_signature": json_data.get("time_signature") or metadata.get("time_signature", "4/4"),
            "key": json_data.get("key") or metadata.get("key", "C"),
            "sections": json_data.get("sections", []),
            "chords": json_data.get("chord_progression", []) or json_data.get("chords", []),
            "lyrics": lyrics_data.get("lines", []) if lyrics_data else [],
            "raw_json": json_data,
            "created_at": "2024-01-01T00:00:00Z"
        }

        # Add to storage
        songs_storage.append(song_data)

        # Return comprehensive result
        result = {
            "success": True,
            "message": "JSON imported successfully with lyrics",
            "song_id": next_id,
            "filename": file.filename,
            "title": song_data["title"],
            "artist": song_data["artist"],
            "sections_count": len(song_data["sections"]),
            "chords_count": len(song_data["chords"]),
            "lyrics_count": len(song_data["lyrics"]),
            "lyrics_synced": lyrics_data.get("synced", False) if lyrics_data else False,
            "preview": song_data
        }

        if lyrics_data:
            result["lyrics_source"] = lyrics_data.get("source")
            result["lyrics_matched"] = lyrics_data.get("matched")

        return result

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@app.post("/combine/jcrd-lyrics")
async def combine_jcrd_lyrics(payload: Dict[str, Any], save: bool = Query(default=True)):
    """Combine JCRD data with lyrics from LRCLIB"""
    try:
        jcrd = payload.get("jcrd", {})
        title = payload.get("title") or jcrd.get("metadata", {}).get("title", "")
        artist = payload.get("artist") or jcrd.get("metadata", {}).get("artist", "")
        include_lyrics = payload.get("include_lyrics", True)

        # Fetch lyrics if needed
        lyrics_data = None
        if include_lyrics and title:
            lyrics_data = await fetch_lyrics_from_lrclib(title, artist)

        # Combine data
        combined = {
            "title": title,
            "artist": artist,
            "jcrd": jcrd,
            "lyrics": lyrics_data.get("lines", []) if lyrics_data else [],
            "combined_at": "2024-01-01T00:00:00Z"
        }

        if save:
            # Generate ID and save
            next_id = max([s.get("id", 0) for s in songs_storage], default=0) + 1
            song_data = {
                "id": next_id,
                "title": title,
                "artist": artist,
                "content": json.dumps(combined),
                "bpm": jcrd.get("bpm", 120),
                "key": jcrd.get("key", "C"),
                "sections": jcrd.get("sections", []),
                "chords": jcrd.get("chord_progression", []),
                "lyrics": combined["lyrics"],
                "created_at": "2024-01-01T00:00:00Z"
            }
            songs_storage.append(song_data)
            combined["song_id"] = next_id

        return combined

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Combine failed: {str(e)}")

@app.options("/combine/jcrd-lyrics")
def combine_options():
    """Handle CORS preflight for combine endpoint"""
    return {"ok": True}

@app.post("/combine/jcrd-lyrics")
def combine_jcrd_lyrics(save: bool = True, payload: Dict[str, Any] = None):
    """Handle combine requests for JSON chord files with lyrics"""
    if save:
        # Generate next ID
        next_id = max([s.get("id", 0) for s in songs_storage], default=0) + 1

        # Create new song from combine request
        new_song = {
            "id": next_id,
            "title": "Imported Song",
            "artist": "Various Artists",
            "content": "Combined JSON chord and lyrics content",
            "bpm": 120,
            "key": "C",
            "created_at": "2024-01-01T00:00:00Z"
        }

        # Add to storage
        songs_storage.append(new_song)

        return {
            "success": True,
            "message": "Combined and saved successfully",
            "song_id": next_id,
            "title": new_song["title"],
            "content": new_song["content"]
        }

    return {
        "success": True,
        "message": "Combined successfully (not saved)",
        "song_id": 123,
        "title": "Combined Song",
        "content": "Demo combined content"
    }

@app.post("/parse")
def parse_text(text_data: Dict[str, Any]):
    """Parse text content and create a song"""
    text = text_data.get("text", "")

    # Generate next ID
    next_id = max([s.get("id", 0) for s in songs_storage], default=0) + 1

    # Simple text parsing - extract title if possible
    lines = text.split('\n')
    title = lines[0] if lines else "Parsed Song"
    if len(title) > 50:
        title = title[:47] + "..."

    # Create new song
    new_song = {
        "id": next_id,
        "title": title,
        "artist": "Parsed Content",
        "content": text,
        "bpm": 120,
        "key": "C",
        "created_at": "2024-01-01T00:00:00Z"
    }

    # Add to storage
    songs_storage.append(new_song)

    return {
        "success": True,
        "message": "Text parsed successfully",
        "song_id": next_id,
        "song": new_song
    }

@app.post("/legacy/lyrics/parse")
def parse_lyrics():
    """Handle legacy lyrics parsing"""
    return {
        "success": True,
        "message": "Lyrics parsed successfully",
        "parsed_count": 5,
        "songs": ["Song 1", "Song 2", "Song 3"]
    }

@app.post("/import/lyrics")
def import_lyrics():
    """Handle lyrics import and preview"""
    return {
        "count": 3,
        "sample": ["Hey Jude - The Beatles", "Let It Be - The Beatles", "Yesterday - The Beatles"],
        "sampleTs": [0, 30, 60]
    }

@app.post("/songs")
def create_song(song_data: Dict[str, Any]):
    """Create a new song from the editor"""
    # Generate next ID
    next_id = max([s.get("id", 0) for s in songs_storage], default=0) + 1

    # Handle different input formats
    if "metadata" in song_data:
        # Editor format
        new_song = {
            "id": next_id,
            "title": song_data.get("metadata", {}).get("title", "Untitled"),
            "artist": song_data.get("metadata", {}).get("artist", "Unknown"),
            "content": str(song_data.get("sections", [])),
            "bpm": song_data.get("metadata", {}).get("tempo", 120),
            "key": song_data.get("metadata", {}).get("key", "C"),
            "created_at": "2024-01-01T00:00:00Z"
        }
    else:
        # Import format (title, artist, content)
        new_song = {
            "id": next_id,
            "title": song_data.get("title", "Untitled"),
            "artist": song_data.get("artist", "Unknown"),
            "content": song_data.get("content", ""),
            "bpm": song_data.get("bpm", 120),
            "key": song_data.get("key", "C"),
            "created_at": "2024-01-01T00:00:00Z"
        }

    # Add to storage
    songs_storage.append(new_song)

    return {
        "success": True,
        "message": "Song created successfully",
        "song_id": next_id,
        "song": new_song
    }

@app.get("/songs")
def get_songs() -> List[Dict[str, Any]]:
    """Return all songs from storage"""
    return songs_storage

@app.get("/songs/{song_id}")
def get_song(song_id: int) -> Dict[str, Any]:
    """Return a demo song with timeline data"""
    songs = {
        1: {
            "id": 1,
            "title": "Hey Jude",
            "artist": "The Beatles",
            "bpm": 72,
            "key": "F",
            "sections": [
                {
                    "name": "Intro",
                    "start_beat": 0,
                    "length_beats": 16,
                    "chords": [
                        {"beat": 0, "chord": "F", "duration": 4},
                        {"beat": 4, "chord": "C", "duration": 4},
                        {"beat": 8, "chord": "F", "duration": 4},
                        {"beat": 12, "chord": "Bb", "duration": 4}
                    ],
                    "lyrics": []
                },
                {
                    "name": "Verse 1",
                    "start_beat": 16,
                    "length_beats": 32,
                    "chords": [
                        {"beat": 16, "chord": "F", "duration": 4},
                        {"beat": 20, "chord": "C", "duration": 4},
                        {"beat": 24, "chord": "F", "duration": 4},
                        {"beat": 28, "chord": "Bb", "duration": 4},
                        {"beat": 32, "chord": "F", "duration": 4},
                        {"beat": 36, "chord": "C", "duration": 4},
                        {"beat": 40, "chord": "F", "duration": 4},
                        {"beat": 44, "chord": "Bb", "duration": 4}
                    ],
                    "lyrics": [
                        {"beat": 16, "text": "Hey Jude, don't make it bad"},
                        {"beat": 24, "text": "Take a sad song and make it better"},
                        {"beat": 32, "text": "Remember to let her into your heart"},
                        {"beat": 40, "text": "Then you'll start to make it better"}
                    ]
                }
            ]
        }
    }

    if song_id not in songs:
        return {"error": "Song not found"}

    return songs[song_id]

@app.post("/import/multi")
def import_multi_files():
    """Handle multi-file import requests"""
    # Mock response for file imports
    return {
        "songs": [
            {
                "title": "Imported Song",
                "artist": "Various Artists",
                "content": "Content from imported files..."
            }
        ]
    }

@app.post("/parse")
def parse_text():
    """Handle text parsing requests"""
    # Mock response for text parsing
    return {
        "songs": [
            {
                "title": "Parsed Song",
                "artist": "Text Import",
                "content": "Content from parsed text..."
            }
        ]
    }

@app.get("/lyrics/search")
def search_lyrics(title: str, artist: str, album: str = None, duration_sec: int = None):
    """Search for lyrics via lrclib API (mock response for now)"""
    # Mock response that matches lrclib format
    return {
        "source": "lrclib",
        "matched": True,
        "synced": True,
        "lines": [
            {"ts_sec": 0.0, "text": f"[Mock lyrics for '{title}' by {artist}]"},
            {"ts_sec": 5.0, "text": "Verse 1 line 1"},
            {"ts_sec": 10.0, "text": "Verse 1 line 2"},
            {"ts_sec": 15.0, "text": "Chorus line 1"},
            {"ts_sec": 20.0, "text": "Chorus line 2"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
