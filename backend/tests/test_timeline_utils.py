import math
import pytest

from app.utils.timeline import seconds_to_beats, beats_to_bars, quantize_beats, align_chords_to_grid


def test_seconds_to_beats_basic():
    # 120 bpm -> 2 beats per second
    beats = seconds_to_beats(30.0, bpm=120.0, time_signature="4/4")
    assert math.isclose(beats, 60.0, rel_tol=1e-6)


def test_beats_to_bars_4_4():
    # 4 beats per bar; beat position 10.0 -> bar 3 beat 2.0 (0-based beat-in-bar)
    bar, beat = beats_to_bars(10.0, time_signature="4/4")
    assert (bar, beat) == (3, 2.0)


def test_beats_to_bars_3_4():
    bar, beat = beats_to_bars(7.5, time_signature="3/4")
    # 3 beats per bar -> 7.5 -> bar 3 (since bars 0-1: 0-2.999, 1:3-5.999, 2:6-8.999), beat 1.5
    assert (bar, beat) == (3, 1.5)


def test_quantize_beats_grids():
    # grid 1/4 -> step 1.0 beat; 1/8 -> step 0.5 beat
    vals = [0.1, 0.49, 0.51, 0.76, 1.24]
    q_quarter = [quantize_beats(v, grid="1/4") for v in vals]
    q_eighth = [quantize_beats(v, grid="1/8") for v in vals]
    assert q_quarter == [0.0, 0.0, 1.0, 1.0, 1.0]
    assert q_eighth == [0.0, 0.5, 0.5, 1.0, 1.0]


def test_align_chords_to_grid_snap():
    chords = [
        {"name": "C", "startBeat": 0.12},
        {"name": "G", "startBeat": 1.26},
        {"name": "Am", "startBeat": 2.74},
    ]
    out = align_chords_to_grid(chords, grid="1/8")
    assert [c["startBeat"] for c in out] == [0.0, 1.5, 2.5]
    # preserve names
    assert [c["name"] for c in out] == ["C", "G", "Am"]
