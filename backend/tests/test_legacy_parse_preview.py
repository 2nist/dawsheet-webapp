from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_legacy_preview_endpoint_text_plain():
    r = client.post("/legacy/lyrics/parse", data="Line 1\nLine 2")
    assert r.status_code == 200
    data = r.json()
    assert "lines" in data
    assert len(data["lines"]) == 2
    assert data["lines"][0]["text"] == "Line 1"
