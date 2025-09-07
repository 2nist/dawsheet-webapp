from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _parse_time_signature(ts: str | None) -> Tuple[int, int]:
    if not ts or "/" not in ts:
        return 4, 4
    try:
        num_s, den_s = ts.split("/", 1)
        num = int(num_s.strip())
        den = int(den_s.strip())
        if num <= 0 or den <= 0:
            return 4, 4
        return num, den
    except Exception:
        return 4, 4


def _quarter_beats_per_bar(num: int, den: int) -> float:
    return num * (4.0 / den)


def _qbpm_from_tempo_and_ts(tempo: float | int | None, den: int) -> float:
    if not tempo or tempo <= 0:
        tempo = 120.0
    return float(tempo) * (4.0 / den)


def _sec_to_qbeats(seconds: float, qbpm: float) -> float:
    return seconds * (qbpm / 60.0)


def _format_pos(qbeats: float, qbeats_per_bar: float) -> Dict[str, float | int]:
    if qbeats < 0:
        qbeats = 0.0
    bar_float = qbeats / qbeats_per_bar if qbeats_per_bar > 0 else 0.0
    bar_index0 = int(bar_float)
    start_bar = bar_index0 + 1
    beat_in_bar = (qbeats - bar_index0 * qbeats_per_bar) + 1.0
    return {
        "bar": start_bar,
        "beat_in_bar": round(beat_in_bar, 3),
    }


def convert_jcrd(obj: Dict[str, Any]) -> Dict[str, Any]:
    meta = obj.get("metadata") or {}
    tempo = meta.get("tempo") or meta.get("bpm")
    time_sig = meta.get("time_signature")
    num, den = _parse_time_signature(str(time_sig) if time_sig else None)
    qbpm = _qbpm_from_tempo_and_ts(tempo, den)
    qpb = _quarter_beats_per_bar(num, den)

    def conv_sec(v: float) -> float:
        return round(float(v), 6)

    def conv_q(v: float) -> float:
        return round(_sec_to_qbeats(float(v), qbpm), 6)

    out: Dict[str, Any] = {
        "metadata": {
            **meta,
            "bpm": float(tempo) if tempo else 120.0,
            "qbpm": round(qbpm, 6),
            "time_signature": f"{num}/{den}",
            "quarter_beats_per_bar": round(qpb, 6),
        }
    }

    sections: List[Dict[str, Any]] = []
    for sec in obj.get("sections", []) or []:
        chords_out: List[Dict[str, Any]] = []
        for ch in sec.get("chords", []) or []:
            st = float(ch.get("start_time", 0.0))
            et = float(ch.get("end_time", st))
            start_q = _sec_to_qbeats(st, qbpm)
            end_q = _sec_to_qbeats(et, qbpm)
            dur_q = end_q - start_q
            dur_bars = dur_q / qpb if qpb > 0 else 0.0
            pos = _format_pos(start_q, qpb)
            chords_out.append({
                "chord": ch.get("chord"),
                "start_sec": conv_sec(st),
                "end_sec": conv_sec(et),
                "start_qbeats": round(start_q, 6),
                "end_qbeats": round(end_q, 6),
                "duration_qbeats": round(dur_q, 6),
                "duration_bars": round(dur_bars, 6),
                "start_bar": pos["bar"],
                "start_beat_in_bar": pos["beat_in_bar"],
            })
        sections.append({
            "name": sec.get("name"),
            "start_sec": conv_sec(sec.get("start_time", 0.0)),
            "end_sec": conv_sec(sec.get("end_time", 0.0)),
            "chords": chords_out,
        })
    if sections:
        out["sections"] = sections

    progression_out: List[Dict[str, Any]] = []
    for it in obj.get("chord_progression", []) or []:
        st = float(it.get("time", 0.0))
        dur = float(it.get("duration", 0.0))
        start_q = _sec_to_qbeats(st, qbpm)
        dur_q = _sec_to_qbeats(dur, qbpm)
        dur_bars = dur_q / qpb if qpb > 0 else 0.0
        pos = _format_pos(start_q, qpb)
        progression_out.append({
            "chord": it.get("chord"),
            "start_sec": conv_sec(st),
            "start_qbeats": round(start_q, 6),
            "start_bar": pos["bar"],
            "start_beat_in_bar": pos["beat_in_bar"],
            "duration_sec": conv_sec(dur),
            "duration_qbeats": round(dur_q, 6),
            "duration_bars": round(dur_bars, 6),
        })
    if progression_out:
        out["chord_progression"] = progression_out

    return out
