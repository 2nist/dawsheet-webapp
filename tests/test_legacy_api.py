from starlette.testclient import TestClient
from backend.app.main import app


client = TestClient(app)


def test_legacy_ping():
    r = client.get("/legacy/ping")
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True
    assert j.get("service") == "legacy"


def test_legacy_parse_lines_shape():
    text = "Hello\nWorld\n"
    r = client.post("/legacy/lyrics/parse", data=text, headers={"content-type": "text/plain"})
    assert r.status_code == 200
    j = r.json()
    assert "lines" in j and isinstance(j["lines"], list)
    assert len(j["lines"]) == 2
    assert j["lines"][0]["text"] == "Hello" and j["lines"][1]["text"] == "World"
