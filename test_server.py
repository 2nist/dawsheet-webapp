"""
Minimal Test Server for DAWSheet
Testing basic connectivity without complex frameworks
"""
import socket
import threading
import time
import json
from datetime import datetime

def handle_client(client_socket, address):
    """Handle incoming client connections"""
    try:
        print(f"Connection from {address}")

        # Receive the request
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Request: {request.split()[0:2] if request else 'Empty'}")

        # Parse the request
        if 'GET' in request:
            if '/api/health' in request:
                response_data = {"status": "healthy", "timestamp": datetime.now().isoformat()}
            elif '/api/v1/songs' in request:
                response_data = [
                    {
                        "id": "test-1",
                        "title": "Test Song 1",
                        "artist": "Test Artist",
                        "content": "This is a test song",
                        "metadata": {"test": True}
                    }
                ]
            else:
                response_data = {"message": "DAWSheet Test Server", "status": "running"}
        else:
            response_data = {"error": "Method not supported"}

        # Create HTTP response
        response_json = json.dumps(response_data)
        response = f"""HTTP/1.1 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
Content-Length: {len(response_json)}

{response_json}"""

        client_socket.send(response.encode('utf-8'))
        print(f"Response sent to {address}")

    except Exception as e:
        print(f"Error handling client {address}: {e}")
        error_response = """HTTP/1.1 500 Internal Server Error
Content-Type: application/json
Access-Control-Allow-Origin: *

{"error": "Internal server error"}"""
        try:
            client_socket.send(error_response.encode('utf-8'))
        except:
            pass
    finally:
        client_socket.close()

def start_test_server(host='localhost', port=8000):
    """Start the test server"""
    try:
        # Create socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind and listen
        server_socket.bind((host, port))
        server_socket.listen(5)

        print(f"🌐 DAWSheet Test Server starting...")
        print(f"📍 Server listening on http://{host}:{port}")
        print(f"🔧 Health check: http://{host}:{port}/api/health")
        print(f"📋 Songs API: http://{host}:{port}/api/v1/songs")
        print("Press Ctrl+C to stop")

        while True:
            try:
                # Accept connections
                client_socket, address = server_socket.accept()

                # Handle in a separate thread
                client_thread = threading.Thread(
                    target=handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()

            except KeyboardInterrupt:
                print("\n🛑 Server stopped by user")
                break
            except Exception as e:
                print(f"Error accepting connection: {e}")

    except Exception as e:
        print(f"❌ Failed to start server: {e}")
    finally:
        try:
            server_socket.close()
        except:
            pass

if __name__ == "__main__":
    start_test_server()
