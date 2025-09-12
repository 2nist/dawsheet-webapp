#!/usr/bin/env python3
"""
Simple HTTP server test - no external dependencies
"""
import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs

PORT = 8001

class DAWSheetHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if self.path == '/api/health':
            response = {"status": "healthy"}
        elif self.path == '/songs' or self.path == '/api/v1/songs':
            response = [
                {"id": "1", "title": "Demo Song 1", "artist": "Demo Artist"},
                {"id": "2", "title": "Demo Song 2", "artist": "Another Artist"}
            ]
        else:
            response = {"message": "DAWSheet Simple Server", "status": "running"}

        self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    print(f"🚀 Starting DAWSheet Simple Server on port {PORT}...")
    print(f"📍 API: http://localhost:{PORT}")
    print(f"🔧 Health: http://localhost:{PORT}/api/health")
    print("Press Ctrl+C to stop")

    with socketserver.TCPServer(("", PORT), DAWSheetHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
            httpd.shutdown()
