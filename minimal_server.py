from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/v1/songs/{song_id}/doc")
def get_song_doc(song_id: int):
    """Return song document data"""
    return {
        "id": song_id,
        "title": f"Song {song_id}",
        "content": "Demo content",
        "sections": []
    }

@app.post("/import/json")
def import_json(json_data: Dict[str, Any], include_lyrics: bool = True):
    """Handle JSON import requests"""
    # Generate next ID
    next_id = max([s.get("id", 0) for s in songs_storage], default=0) + 1

    # Extract song data from JSON
    title = json_data.get("title", "Imported Song")
    artist = json_data.get("artist", "Unknown Artist")
    content = str(json_data)  # Store the full JSON as content

    # Create new song
    new_song = {
        "id": next_id,
        "title": title,
        "artist": artist,
        "content": content,
        "bpm": json_data.get("bpm", 120),
        "key": json_data.get("key", "C"),
        "created_at": "2024-01-01T00:00:00Z"
    }

    # Add to storage
    songs_storage.append(new_song)

    return {
        "success": True,
        "message": "JSON imported successfully",
        "song_id": next_id,
        "parsed_data": json_data if include_lyrics else None
    }

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
