from starlette.testclient import TestClient
from backend.app.main import app


client = TestClient(app)


def test_legacy_ping():
    r = client.get("/legacy/ping")
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True
    assert j.get("service") == "legacy"


def test_legacy_parse_stub():
    text = "Hello\nWorld\n"
    r = client.post("/legacy/lyrics/parse", data=text, headers={"content-type": "text/plain"})
    assert r.status_code == 200
    j = r.json()
    assert "songs" in j and isinstance(j["songs"], list)
    assert len(j["songs"]) == 1
    sections = j["songs"][0].get("sections")
    assert sections and len(sections) == 1
    lines = sections[0].get("lines")
    assert lines and len(lines) == 2
    assert lines[0]["text"] == "Hello" and lines[1]["text"] == "World"
