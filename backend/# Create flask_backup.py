# Create flask_backup.py
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def root():
    return jsonify({"message": "DAWSheet API", "version": "1.0.0"})

@app.route('/songs')
def get_songs():
    return jsonify([{"id": 1, "title": "Test Song", "artist": "Test Artist"}])

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)