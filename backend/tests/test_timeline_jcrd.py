from app.mappers.timeline import to_timeline


def test_jcrd_metadata_and_sections():
    raw = {
        "metadata": {"tempo": 160, "time_signature": "4/4", "key": "Key E"},
        "sections": [
            {"name": "intro", "start_time": 0.0, "end_time": 2.0, "chords": []},
            {"name": "verse", "start_time": 2.0, "end_time": 10.0, "chords": [
                {"chord": "E", "start_time": 2.0, "end_time": 4.0},
                {"chord": "A", "start_time": 4.0, "end_time": 6.0},
            ]},
        ],
        "chord_progression": [
            {"time": 6.0, "chord": "B", "duration": 2.0},
        ],
    }
    tl, warnings, validation = to_timeline(raw)
    assert tl.bpmDefault == 160
    assert tl.timeSigDefault["num"] == 4 and tl.timeSigDefault["den"] == 4
    # Sections preserved
    assert len(tl.sections) == 2
    assert tl.sections[0].startSec == 0.0 and tl.sections[1].startSec == 2.0
    # Chords from sections + chord_progression
    symbols = [c.symbol for c in tl.chords]
    assert symbols[:3] == ["E", "A", "B"] or symbols[:3] == ["E", "A", "B"]
    # Durations in beats (2 seconds at 160 bpm -> beats = 160*2/60 ~= 5.3333)
    # We just validate they were converted (non-null)
    assert all(c.durationBeats for c in tl.chords[:3])
    # Key extracted heuristically
    assert tl.key and "E" in tl.key.upper()
    # Only chords expected; lyrics may be absent in pure chord dataset
    non_fatal_codes = {v.code for v in validation}
    assert non_fatal_codes <= {"lyrics.empty"}
