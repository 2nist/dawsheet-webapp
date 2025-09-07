from __future__ import annotations

from typing import Dict, List, Tuple, Any, Optional


def seconds_to_beats(seconds: float, bpm: float, time_signature: Optional[str] = None) -> float:
    if bpm <= 0:
        bpm = 120.0
    return float(seconds) * (bpm / 60.0)


def beats_to_bars(beats: float, time_signature: str) -> Tuple[int, float]:
    try:
        num_s, den_s = str(time_signature).split("/", 1)
        num = max(1, int(num_s))
        den = max(1, int(den_s))
    except Exception:
        num, den = 4, 4
    qpb = num * (4.0 / den)
    if qpb <= 0:
        qpb = num
    bars_float = beats / qpb
    bar_index0 = int(bars_float)
    beat_in_bar = (beats - bar_index0 * qpb)
    return bar_index0 + 1, round(beat_in_bar, 4)


def _grid_step(grid: str) -> float:
    """Grid like '1/4','1/8' in musical terms relative to a quarter-note = 1 beat.
    '1/4' -> 1.0 beat, '1/8' -> 0.5 beat, '1/16' -> 0.25 beat.
    """
    try:
        _, d = grid.split("/", 1)
        div = int(d)
        if div <= 0:
            return 0.0
        return 4.0 / div
    except Exception:
        return 0.0


def quantize_beats(beats: float, grid: str) -> float:
    step = _grid_step(grid)
    if step <= 0:
        return beats
    return round(beats / step) * step


def align_chords_to_grid(
    chords: List[Dict[str, Any]],
    *,
    bpm: Optional[float] = None,
    time_sig: Optional[str] = None,
    grid: str = "1/4",
) -> List[Dict[str, Any]]:
    """Return new chord list with startBeat quantized and optional bar/beat annotations.

    Accepts either:
    - items with precomputed 'startBeat', or
    - items with seconds ('start_sec' or 'time') plus provided bpm/time_sig.
    """
    out: List[Dict[str, Any]] = []
    for ch in chords or []:
        if "startBeat" in ch and ch["startBeat"] is not None:
            beats_val = float(ch["startBeat"])
        else:
            st_s = float(ch.get("start_sec") or ch.get("time") or 0.0)
            if bpm is None:
                # cannot convert reliably; assume seconds are already beats
                beats_val = st_s
            else:
                beats_val = seconds_to_beats(st_s, bpm)
        qb = quantize_beats(beats_val, grid)
        item = {**ch, "startBeat": round(qb, 4)}
        if time_sig:
            bar, beat_in_bar = beats_to_bars(qb, time_sig)
            item.update({"bar": bar, "beat_in_bar": round(beat_in_bar, 3)})
        out.append(item)
    return out
