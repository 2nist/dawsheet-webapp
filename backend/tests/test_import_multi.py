from pathlib import Path
import sys
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))
from app.main import app  # type: ignore


client = TestClient(app)


def test_import_multi_mixed_text_and_json():
    txt = "Line1\nLine2"
    j = {"title": "Song A", "artist": "X", "content": "C"}
    files = [
        ("files", ("a.txt", txt, "text/plain")),
        ("files", ("song.json", json_bytes := bytes(str(j).replace("'", '"'), "utf-8"), "application/json")),
    ]
    r = client.post("/import/multi", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert isinstance(body.get("songs"), list)
    assert body["counts"]["input_files"] == 2
