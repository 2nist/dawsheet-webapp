"""
Simple HTTP Server for DAWSheet
Uses Python's built-in http.server as a more stable alternative
"""
import json
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

# Simple in-memory storage
songs_storage = {}

class DAWSheetHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _json_response(self, data, status=200):
        self._set_headers(status)
        response = json.dumps(data, default=str)
        self.wfile.write(response.encode())

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            if path == "/" or path == "/api/health":
                self._json_response({"status": "healthy", "songs_count": len(songs_storage)})
            elif path == "/songs" or path == "/api/v1/songs":
                self._json_response(list(songs_storage.values()))
            elif path.startswith("/api/v1/songs/"):
                song_id = path.split("/")[-1]
                if song_id in songs_storage:
                    self._json_response(songs_storage[song_id])
                else:
                    self._json_response({"error": "Song not found"}, 404)
            else:
                self._json_response({"error": "Not found"}, 404)
        except Exception as e:
            print(f"Error in GET {path}: {e}")
            self._json_response({"error": str(e)}, 500)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            if path == "/songs" or path == "/api/v1/songs":
                # Create new song
                song_id = str(uuid.uuid4())
                now = datetime.now()

                new_song = {
                    "id": song_id,
                    "title": data.get("title", "Untitled"),
                    "artist": data.get("artist", "Unknown"),
                    "content": data.get("content", ""),
                    "metadata": data.get("metadata", {}),
                    "created_at": now,
                    "updated_at": now
                }

                songs_storage[song_id] = new_song
                self._json_response(new_song)
            else:
                self._json_response({"error": "Not found"}, 404)
        except Exception as e:
            print(f"Error in POST {path}: {e}")
            self._json_response({"error": str(e)}, 500)

def add_demo_songs():
    """Add demo songs to storage"""
    demo_songs = [
        {
            "title": "HTTP Demo Song 1",
            "artist": "HTTP Artist",
            "content": "This is an HTTP server demo song",
            "metadata": {"demo": True, "server": "http"}
        },
        {
            "title": "HTTP Demo Song 2",
            "artist": "Another HTTP Artist",
            "content": "Another HTTP server demo song",
            "metadata": {"demo": True, "server": "http"}
        }
    ]

    for song_data in demo_songs:
        song_id = str(uuid.uuid4())
        now = datetime.now()

        new_song = {
            "id": song_id,
            "title": song_data["title"],
            "artist": song_data["artist"],
            "content": song_data["content"],
            "metadata": song_data["metadata"],
            "created_at": now,
            "updated_at": now
        }

        songs_storage[song_id] = new_song

    print(f"✅ Added {len(demo_songs)} demo songs to HTTP server")

def run_server():
    """Run the HTTP server"""
    try:
        # Add demo data
        add_demo_songs()

        # Create and start server
        server_address = ('', 8000)
        httpd = HTTPServer(server_address, DAWSheetHandler)

        print("🌐 DAWSheet HTTP Server starting...")
        print("📍 Server running at: http://localhost:8000")
        print("🔧 Health check: http://localhost:8000/api/health")
        print("📋 Songs API: http://localhost:8000/api/v1/songs")
        print("Press Ctrl+C to stop the server")

        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    run_server()
