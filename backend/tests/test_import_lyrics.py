import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure we can import backend FastAPI app by adding backend/app to sys.path
ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))
from app.main import app  # type: ignore


client = TestClient(app)


def test_import_lyrics_txt():
    data = "Hello\nWorld"
    files = {"file": ("sample.txt", data, "text/plain")}
    r = client.post("/import/lyrics", files=files)
    assert r.status_code == 200
    j = r.json()
    assert j["ok"] is True
    assert len(j["items"]) == 2
    assert j["items"][0]["line"] == "Hello"
    assert j["items"][0]["timestamp"] is None


def test_import_lyrics_lrc():
    data = """[00:10.5] Line A\n[00:12.000] Line B"""
    files = {"file": ("song.lrc", data, "text/plain")}
    r = client.post("/import/lyrics", files=files)
    assert r.status_code == 200
    j = r.json()
    ts = [it.get("timestamp") for it in j["items"]]
    assert any(abs(t - 10.5) < 0.001 for t in ts if t is not None)
import io
import json
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.legacy.ingest.lyrics import parse_lyrics_payload


client = TestClient(app)


def test_utils_parse_lrc_basic():
    text = """[00:05.10] Hello
[00:07.00]World"""
    lines = parse_lyrics_payload(text, "song.lrc")
    assert len(lines) == 2
    assert lines[0].text == "Hello"
    assert abs(lines[0].ts - 5.1) < 1e-6


def test_utils_parse_vtt_basic():
    text = """WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nHello\n00:00:02.500 --> 00:00:03.000\nWorld"""
    lines = parse_lyrics_payload(text, "song.vtt")
    assert len(lines) >= 2
    assert lines[0].text.lower().startswith("hello")


def test_import_lyrics_endpoint_txt():
    resp = client.post(
        "/import/lyrics",
        files={"file": ("plain.txt", b"Line A\nLine B", "text/plain")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert len(data.get("items", [])) == 2
    assert data["items"][0]["line"] == "Line A"
    assert data["items"][0]["timestamp"] is None


def test_import_multi_mixed_batch():
    # Prepare files: json with one song + txt lyrics
    j = json.dumps({"title": "T1", "artist": "A1", "content": "C1"}).encode()
    resp = client.post(
        "/import/multi",
        files=[
            ("files", ("a.json", j, "application/json")),
            ("files", ("b.txt", b"L1\nL2", "text/plain")),
        ],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["counts"]["input_files"] == 2
    assert isinstance(data.get("songs"), list)
    assert data["counts"]["songs"] >= 2
