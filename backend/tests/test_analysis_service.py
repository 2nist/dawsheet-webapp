from app.services.analysis import analyze_songdoc, analyze_from_content


def test_analyze_songdoc_basic_sections():
    jcrd_like = {
        "title": "Test Song",
        "artist": "Tester",
        "bpm": 120,
        "timeSignature": "4/4",
        "chords": [
            {"name": "C", "startBeat": 0.0},
            {"name": "F", "startBeat": 4.0},
            {"name": "G", "startBeat": 8.0},
            {"name": "C", "startBeat": 12.0},
        ],
        "lyrics": [
            {"text": "Line 1", "startBeat": 0.0},
            {"text": "Line 2", "startBeat": 4.0},
        ],
    }
    doc = analyze_songdoc(jcrd_like)
    assert doc["title"] == "Test Song"
    assert doc["timeSignature"] == "4/4"
    assert "sections" in doc and len(doc["sections"]) >= 1
    assert "issues" in doc


def test_analyze_from_content_parses_simple():
    content = """
| C     | F     |
C F G C
Some lyrics here
More lyrics
""".strip()
    doc = analyze_from_content(title="X", artist="Y", content=content)
    assert doc["title"] == "X"
    assert doc["artist"] == "Y"
    assert "chords" in doc and len(doc["chords"]) >= 1
    assert "sections" in doc
