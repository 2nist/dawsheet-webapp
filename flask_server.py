"""
Flask-based DAWSheet Backend Server
Alternative to FastAPI for better stability
"""
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Simple in-memory storage
songs_storage = {}

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

print("🚀 Initializing DAWSheet Flask Backend...")

def add_demo_songs():
    """Add demo songs to storage"""
    demo_songs = [
        {
            "title": "Flask Demo Song 1",
            "artist": "Flask Artist",
            "content": "This is a Flask demo song",
            "metadata": {"demo": True, "framework": "flask"}
        },
        {
            "title": "Flask Demo Song 2",
            "artist": "Another Flask Artist",
            "content": "Another Flask demo song",
            "metadata": {"demo": True, "framework": "flask"}
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
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }

        songs_storage[song_id] = new_song

    print(f"✅ Added {len(demo_songs)} demo songs")

# Routes
@app.route('/')
def root():
    return jsonify({"message": "DAWSheet Flask API", "version": "1.0.0", "status": "running"})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "songs_count": len(songs_storage)})

@app.route('/health')
def health_simple():
    return jsonify({"status": "ok"})

@app.route('/api/v1/songs', methods=['GET'])
def list_songs():
    try:
        return jsonify(list(songs_storage.values()))
    except Exception as e:
        print(f"Error in list_songs: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/songs', methods=['POST'])
def create_song():
    try:
        data = request.get_json()
        song_id = str(uuid.uuid4())
        now = datetime.now()

        new_song = {
            "id": song_id,
            "title": data.get("title", "Untitled"),
            "artist": data.get("artist", "Unknown"),
            "content": data.get("content", ""),
            "metadata": data.get("metadata", {}),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }

        songs_storage[song_id] = new_song
        return jsonify(new_song)
    except Exception as e:
        print(f"Error in create_song: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/songs/<song_id>', methods=['GET'])
def get_song(song_id):
    try:
        if song_id not in songs_storage:
            return jsonify({"error": "Song not found"}), 404
        return jsonify(songs_storage[song_id])
    except Exception as e:
        print(f"Error in get_song: {e}")
        return jsonify({"error": str(e)}), 500

# Legacy compatibility
@app.route('/songs', methods=['GET'])
def legacy_songs():
    try:
        return jsonify(list(songs_storage.values()))
    except Exception as e:
        print(f"Error in legacy_songs: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/songs', methods=['POST'])
def legacy_create_song():
    try:
        data = request.get_json()
        return create_song()
    except Exception as e:
        print(f"Error in legacy_create_song: {e}")
        return jsonify({"error": str(e)}), 500

# Initialize demo data
add_demo_songs()

def main():
    """Main entry point"""
    try:
        print("🌐 Starting DAWSheet Flask Server...")
        print("📍 Backend will be available at: http://localhost:8000")
        print("🔧 Health check: http://localhost:8000/api/health")
        print("📋 Songs API: http://localhost:8000/api/v1/songs")

        # Run Flask app
        app.run(
            host="0.0.0.0",
            port=8000,
            debug=False,  # Disable debug for stability
            threaded=True
        )
    except Exception as e:
        print(f"❌ Flask server failed to start: {e}")

if __name__ == "__main__":
    main()
