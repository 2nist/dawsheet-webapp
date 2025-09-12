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

@app.post("/songs")
def create_song(song: dict):
    new_song = {"id": str(len(songs) + 1), **song}
    songs.append(new_song)
    return new_song

@app.post("/import/json")
def import_json(data: dict):
    title = data.get("metadata", {}).get("title", "Imported Song")
    artist = data.get("metadata", {}).get("artist", "Unknown Artist")
    new_song = {"id": str(len(songs) + 1), "title": title, "artist": artist}
    songs.append(new_song)
    return {"success": True, "song_id": new_song["id"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
