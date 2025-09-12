#!/usr/bin/env python3
"""
Persistent Backend Server
Uses threading to stay alive
"""
import threading
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="DAWSheet Persistent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

songs = [
    {"id": "1", "title": "Demo Song 1", "artist": "Demo Artist"},
    {"id": "2", "title": "Demo Song 2", "artist": "Another Artist"},
]

@app.get("/")
def root():
    return {"message": "DAWSheet Persistent API", "status": "running"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}

@app.get("/songs")
def get_songs():
    return songs

@app.get("/api/v1/songs")
def get_songs_v1():
    return songs

def keep_alive():
    """Keep the server alive"""
    while True:
        time.sleep(30)
        print("🔄 Server still running...")

def run_server():
    """Run the uvicorn server"""
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    print("🚀 Starting DAWSheet Persistent Server...")
    print("📍 API: http://localhost:8000")
    print("🔧 Health: http://localhost:8000/api/health")
    print("Press Ctrl+C to stop")

    # Start keepalive thread
    keepalive_thread = threading.Thread(target=keep_alive, daemon=True)
    keepalive_thread.start()

    # Run server
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        time.sleep(10)  # Keep terminal open to see error
