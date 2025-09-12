import requests
import sys

try:
    response = requests.get("http://127.0.0.1:8001/api/health", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except requests.exceptions.ConnectionError:
    print("Connection failed - server may not be running")
except Exception as e:
    print(f"Error: {e}")
