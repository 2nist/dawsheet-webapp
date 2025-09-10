from __future__ import annotations

import json
from backend.app.mappers.timeline import to_timeline


def test_jcrd_preserves_bpm_and_section_names():
    jcrd = {
        "metadata": {"title": "Test", "artist": "X", "tempo": 160, "time_signature": "4/4", "key": "Key E"},
        "sections": [
            {"name": "intro", "start_time": 0.0, "end_time": 2.0, "chords": []},
            {"name": "versea", "start_time": 2.0, "end_time": 10.0, "chords": [
                {"chord": "E", "start_time": 2.0, "end_time": 4.0},
                {"chord": "A", "start_time": 4.0, "end_time": 6.0},
            ]},
            {"name": "bridge", "start_time": 10.0, "end_time": 14.0, "chords": [
                {"chord": "B", "start_time": 10.0, "end_time": 12.0},
            ]},
        ],
        "chord_progression": [
            {"time": 2.0, "chord": "E", "duration": 2.0},
            {"time": 4.0, "chord": "A", "duration": 2.0},
            {"time": 10.0, "chord": "B", "duration": 2.0},
        ],
    }
    tl, warnings, validation = to_timeline({**jcrd, "id": 1, "title": "Test", "artist": "X"})
    assert tl.bpmDefault == 160
    assert tl.timeSigDefault == {"num": 4, "den": 4}
    names = [s.name for s in tl.sections]
    assert names[:3] == ["intro", "versea", "bridge"]
    # Ensure kinds normalized but original names kept
    kinds = [s.kind for s in tl.sections[:3]]
    assert kinds == ["Intro", "versea", "Bridge"]
    assert not any(v.code == "bpm.missing" for v in validation)
    assert tl.key and tl.key.upper().startswith("E")
