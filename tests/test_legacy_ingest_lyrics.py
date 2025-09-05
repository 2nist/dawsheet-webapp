from backend.app.legacy.ingest.lyrics import parse_lyrics_payload


def test_parse_txt_basic():
    text = "Hello\nWorld\n"
    out = parse_lyrics_payload(text, filename="a.txt")
    assert len(out) == 2 and out[0].text == "Hello" and out[1].text == "World"
    assert all(l.ts is None for l in out)


def test_parse_lrc_timestamps():
    text = "[00:10.5] Line A\n[00:12.250] Line B\n"
    out = parse_lyrics_payload(text, filename="a.lrc")
    assert len(out) == 2 and out[0].text == "Line A" and out[1].text == "Line B"
    assert abs(out[0].ts - 10.5) < 0.001 and abs(out[1].ts - 12.25) < 0.001


def test_parse_vtt_basic():
    text = "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nHello\n00:00:02.000 --> 00:00:03.000\nWorld\n"
    out = parse_lyrics_payload(text, filename="a.vtt")
    assert len(out) == 2 and out[0].text == "Hello" and out[1].text == "World"
    assert abs(out[0].ts - 1.0) < 0.001 and abs(out[1].ts - 2.0) < 0.001


def test_parse_csv_mixed():
    text = "10.5,Line A\n00:12.250,Line B\nPlain only\n"
    out = parse_lyrics_payload(text, filename="a.csv")
    assert len(out) == 3
    assert abs(out[0].ts - 10.5) < 0.001 and out[0].text == "Line A"
    assert abs(out[1].ts - 12.25) < 0.001 and out[1].text == "Line B"
    assert out[2].ts is None and out[2].text == "Plain only"
