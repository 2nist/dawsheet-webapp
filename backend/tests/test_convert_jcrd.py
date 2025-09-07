import sys, os
sys.path.append('/app')
from app.utils.tempo import convert_jcrd

def test_convert_jcrd_basic():
    sample = {
        "metadata": {"tempo": 120, "time_signature": "4/4"},
        "chord_progression": [
            {"time": 0.0, "chord": "C", "duration": 2.0},  # 2s -> 4 qbeats -> 1 bar
            {"time": 2.0, "chord": "F", "duration": 1.0},  # 1s -> 2 qbeats -> 0.5 bar
        ]
    }
    out = convert_jcrd(sample)
    assert out["metadata"]["qbpm"] == 120.0
    assert out["metadata"]["quarter_beats_per_bar"] == 4.0
    prog = out["chord_progression"]
    assert prog[0]["start_qbeats"] == 0.0
    assert prog[0]["duration_qbeats"] == 4.0
    assert prog[0]["duration_bars"] == 1.0
    assert prog[0]["start_bar"] == 1
    assert prog[1]["start_qbeats"] == 4.0
    assert prog[1]["duration_qbeats"] == 2.0
    assert prog[1]["start_bar"] == 2
