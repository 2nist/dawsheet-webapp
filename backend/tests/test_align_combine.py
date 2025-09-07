import sys
sys.path.append('/app')

from app.utils.align import merge_jcrd_with_lyrics, chords_only_text  # type: ignore


def _jcrd_prog(tempo=120, ts='4/4', events=None):
    if events is None:
        events = []
    return {
        "metadata": {"tempo": tempo, "time_signature": ts},
        "chord_progression": [
            {"time": st, "chord": ch, "duration": dur} for (st, ch, dur) in events
        ],
    }


def test_downbeat_offset_aligns_first_event():
    # First chord at 1.2s, 120 BPM, 4/4 -> should offset so first bar starts at that event
    jcrd = _jcrd_prog(events=[(1.2, 'C', 2.0), (3.2, 'F', 2.0)])
    res = merge_jcrd_with_lyrics(jcrd, [], bar_start='auto')
    meta = res['metadata']
    assert meta['bar_start'] == 'auto'
    assert meta['qoffset'] > 0
    # Expect at least one line (instrumental) and that its position is bar 1 beat 1.0
    lines = res['lines']
    assert any(ln['text'] == '(instrumental)' for ln in lines)
    first = [ln for ln in lines if ln['text'] == '(instrumental)'][0]
    assert first['bar'] == 1
    assert abs(first['beat_in_bar'] - 1.0) < 1e-6


def test_instrumental_gap_between_lyrics():
    # Chords across 0-6s; lyrics at 0.5s and 3.5s -> gap ~3.0s should create an instrumental line
    jcrd = _jcrd_prog(events=[(0.0, 'C', 2.0), (2.0, 'F', 2.0), (4.0, 'G', 2.0)])
    lyrics = {"lines": [{"ts_sec": 0.5, "text": "Hello"}, {"ts_sec": 3.5, "text": "World"}]}
    res = merge_jcrd_with_lyrics(jcrd, lyrics['lines'], bar_start='auto')
    texts = [ln['text'] for ln in res['lines']]
    assert '(instrumental)' in texts


def test_chords_only_no_lyrics():
    # include_lyrics=False path would call chords_only_text; validate offset aligns first chord
    jcrd = _jcrd_prog(events=[(1.2, 'Am', 2.0), (3.2, 'G', 2.0)])
    res = chords_only_text(jcrd, bar_start='auto')
    meta = res['metadata']
    assert meta['bar_start'] == 'auto'
    assert meta['qoffset'] > 0
    first = res['chords'][0]
    assert first['bar'] == 1
    assert abs(first['beat_in_bar'] - 1.0) < 1e-6
