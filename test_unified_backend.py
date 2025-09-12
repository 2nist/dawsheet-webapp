#!/usr/bin/env python3
"""
Test script for the unified DAWSheet backend API
Tests basic CRUD operations and import functionality
"""

import json
import requests
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_DATA_DIR = Path("test_data")

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Health check passed")

def test_songs_crud():
    """Test songs CRUD operations"""
    print("\n🔍 Testing songs CRUD operations...")

    # Test list songs (should be empty initially)
    response = requests.get(f"{BASE_URL}/api/v1/songs")
    assert response.status_code == 200
    initial_songs = response.json()
    print(f"✅ Initial songs count: {len(initial_songs)}")

    # Test create song
    new_song = {
        "title": "Test Song",
        "artist": "Test Artist",
        "content": "Test content for CRUD operations"
    }
    response = requests.post(f"{BASE_URL}/api/v1/songs", json=new_song)
    assert response.status_code == 200
    created_song = response.json()
    song_id = created_song["id"]
    print(f"✅ Created song with ID: {song_id}")

    # Test get specific song
    response = requests.get(f"{BASE_URL}/api/v1/songs/{song_id}")
    assert response.status_code == 200
    retrieved_song = response.json()
    assert retrieved_song["title"] == new_song["title"]
    print("✅ Retrieved song successfully")

    # Test update song
    update_data = {"title": "Updated Test Song"}
    response = requests.put(f"{BASE_URL}/api/v1/songs/{song_id}", json=update_data)
    assert response.status_code == 200
    updated_song = response.json()
    assert updated_song["title"] == "Updated Test Song"
    print("✅ Updated song successfully")

    # Test copy song
    response = requests.post(f"{BASE_URL}/api/v1/songs/{song_id}/copy")
    assert response.status_code == 200
    copied_song = response.json()
    assert "Copy of" in copied_song["title"]
    print(f"✅ Copied song with ID: {copied_song['id']}")

    # Test delete song
    response = requests.delete(f"{BASE_URL}/api/v1/songs/{song_id}")
    assert response.status_code == 200
    print("✅ Deleted original song successfully")

    # Clean up copied song
    requests.delete(f"{BASE_URL}/api/v1/songs/{copied_song['id']}")
    print("✅ Cleaned up copied song")

def test_import_functionality():
    """Test import functionality with Beatles test data"""
    print("\n🔍 Testing import functionality...")

    test_files = ["hey_jude.json", "let_it_be.json", "yesterday.json"]
    imported_songs = []

    for filename in test_files:
        file_path = TEST_DATA_DIR / filename
        if not file_path.exists():
            print(f"⚠️  Test file {filename} not found, skipping")
            continue

        with open(file_path, 'r') as f:
            test_data = json.load(f)

        # Test Isophonics import
        response = requests.post(f"{BASE_URL}/api/v1/import/isophonics", json={"data": test_data})
        if response.status_code != 200:
            print(f"❌ Import failed with status {response.status_code}: {response.text}")
            continue
        result = response.json()
        imported_songs.append(result["song_id"])
        print(f"✅ Imported {test_data['metadata']['title']} via Isophonics format")

        # Test legacy import endpoint
        response = requests.post(f"{BASE_URL}/import/json", json=test_data)
        if response.status_code != 200:
            print(f"❌ Legacy import failed with status {response.status_code}: {response.text}")
            continue
        legacy_result = response.json()
        if legacy_result.get("success"):
            imported_songs.append(legacy_result["song_id"])
            print(f"✅ Imported {test_data['metadata']['title']} via legacy endpoint")
        else:
            print(f"❌ Legacy import failed: {legacy_result.get('error', 'Unknown error')}")

    # Verify all songs were imported
    response = requests.get(f"{BASE_URL}/api/v1/songs")
    all_songs = response.json()
    print(f"✅ Total songs after import: {len(all_songs)}")

    # Clean up imported songs
    for song_id in imported_songs:
        requests.delete(f"{BASE_URL}/api/v1/songs/{song_id}")
    print("✅ Cleaned up all imported songs")

def test_legacy_compatibility():
    """Test legacy endpoint compatibility"""
    print("\n🔍 Testing legacy endpoint compatibility...")

    # Test legacy songs endpoint
    response = requests.get(f"{BASE_URL}/songs")
    assert response.status_code == 200
    print("✅ Legacy /songs endpoint working")

    # Test legacy create song
    new_song = {
        "title": "Legacy Test Song",
        "artist": "Legacy Artist",
        "content": "Test content for legacy compatibility"
    }
    response = requests.post(f"{BASE_URL}/songs", json=new_song)
    assert response.status_code == 200
    created_song = response.json()
    song_id = created_song["id"]
    print(f"✅ Legacy song creation working, ID: {song_id}")

    # Test legacy text parsing
    parse_data = {"text": "Test Song Title\nTest line 1\nTest line 2"}
    response = requests.post(f"{BASE_URL}/parse", json=parse_data)
    assert response.status_code == 200
    parse_result = response.json()
    assert parse_result["success"] is True
    parse_song_id = parse_result["song_id"]
    print(f"✅ Legacy text parsing working, ID: {parse_song_id}")

    # Clean up
    requests.delete(f"{BASE_URL}/api/v1/songs/{song_id}")
    requests.delete(f"{BASE_URL}/api/v1/songs/{parse_song_id}")
    print("✅ Cleaned up legacy test songs")

def main():
    """Run all tests"""
    print("🚀 Starting DAWSheet Backend API Tests")
    print("=" * 50)

    try:
        test_health()
        test_songs_crud()
        test_import_functionality()
        test_legacy_compatibility()

        print("\n" + "=" * 50)
        print("🎉 All tests passed successfully!")
        print("✅ Unified backend is working correctly")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("Please ensure the backend is running on http://localhost:8000")
        return 1
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
