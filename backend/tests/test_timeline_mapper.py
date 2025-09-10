from app.mappers.timeline import to_timeline


def test_to_timeline_quantization_and_duration_inference():
    raw = {
        "id": 1,
        "title": "Test",
        "artist": "X",
        "bpm": 120,
        "timeSignature": "4/4",
        # chord start times slightly off grid; expect quantize to nearest 0.25 beat (quarter-beat)
        "chords": [
            {"symbol": "C", "start_sec": 0.0},        # beat 0.0
            {"symbol": "G", "start_sec": 0.49},       # 0.49s *2 beats/sec = 0.98 -> quantize 1.0
            {"symbol": "Am", "start_sec": 1.01},      # 1.01s *2 = 2.02 -> 2.0
            {"symbol": "F", "start_sec": 1.51},       # 1.51s *2 = 3.02 -> 3.0
        ],
        "lyrics": [
            {"text": "Line 1", "ts_sec": 0.1},
            {"text": "Line 2", "ts_sec": 1.0},
        ],
    }
    timeline, warnings, validation = to_timeline(raw)
    assert not validation, f"Unexpected validation errors: {validation}"
    beats = [c.atBeat for c in timeline.chords]
    assert beats == [0.0, 1.0, 2.0, 3.0]
    # Durations inferred from next chord (except last which may remain None)
    durations = [c.durationBeats for c in timeline.chords]
    assert durations[0] == 1.0 and durations[1] == 1.0 and durations[2] == 1.0
    # Last chord duration may be None or >= 0.25 depending on heuristic; accept either
    assert durations[3] is None or durations[3] >= 0.25
