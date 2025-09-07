from __future__ import annotations

from typing import Any, Dict, List, Optional
import re

from .tempo import _parse_time_signature, _qbpm_from_tempo_and_ts, _sec_to_qbeats, _quarter_beats_per_bar, _format_pos


def _make_group_grid_line(group_start: int, num_beats: int, bars_in_group: int, beat_cells: int = 3) -> str:
    """Create a grid line like "1 |...|...|...|... |...|...|...|..." for the group."""
    bar_pattern = "".join(["|" + ("." * beat_cells) for _ in range(num_beats)])
    body = " ".join([bar_pattern for _ in range(max(1, bars_in_group))])
    return f"{group_start} {body}"


def _aligned_chord_header(
    chords: List[Dict[str, Any]],
    group_start: int,
    num_beats: int,
    bars_in_group: int,
    beat_cells: int = 3,
) -> str:
    """Render chord names aligned to the bar/beat grid for the group's span.
    Only chords whose bar falls within [group_start, group_start+bars_in_group) are placed.
    """
    prefix = f"{group_start} "
    bar_len = num_beats * (1 + beat_cells)
    total_len = len(prefix) + (bar_len + 1) * max(1, bars_in_group) - 1  # minus trailing space
    buf = [" "] * total_len
    # place chords
    for c in chords or []:
        b = c.get("bar")
        bi = c.get("beat_in_bar")
        name = c.get("chord")
        if not (isinstance(b, int) and isinstance(bi, (int, float)) and name):
            continue
        if b < group_start or b >= group_start + max(1, bars_in_group):
            continue
        bar_index = b - group_start  # 0-based within group
        base = len(prefix) + bar_index * (bar_len + 1)
        # beat index is 1..num_beats, + fractional .5 supported
        beat_whole = int(max(1, min(num_beats, int(bi))))
        frac = float(bi) - float(int(bi))
        # If exactly on beat (or very close), place on the '|' character itself.
        if abs(frac) <= 0.05:
            pos = base + (beat_whole - 1) * (1 + beat_cells)
        else:
            # inside the beat cell after '|'
            pos = base + (beat_whole - 1) * (1 + beat_cells) + 1
            pos += int(round(max(0.0, min(1.0, frac)) * beat_cells))
        # write chord name into buffer if space; overwrite dots/spaces safely
        for i, ch in enumerate(str(name)):
            j = pos + i
            if j >= total_len:
                break
            buf[j] = ch
    return "".join(buf).rstrip()


def _collect_chord_segments(jcrd: Dict[str, Any]) -> List[Dict[str, Any]]:
    segs: List[Dict[str, Any]] = []
    # Prefer chord_progression if present
    for it in jcrd.get("chord_progression", []) or []:
        st = float(it.get("time", 0.0))
        dur = float(it.get("duration", 0.0))
        segs.append({
            "start_sec": st,
            "end_sec": st + dur,
            "chord": it.get("chord"),
        })
    if segs:
        return segs
    # Fallback to sections[].chords
    for sec in jcrd.get("sections", []) or []:
        for ch in sec.get("chords", []) or []:
            st = float(ch.get("start_time", 0.0))
            et = float(ch.get("end_time", st))
            segs.append({
                "start_sec": st,
                "end_sec": et,
                "chord": ch.get("chord"),
            })
    # Sort by start time just in case
    segs.sort(key=lambda x: x["start_sec"])
    return segs


def _snap_beat_one_decimal(beat_in_bar: float, num: int) -> float:
    """Snap beat to one decimal, prefer 0.5 increments and bias towards even beats in 4/4.
    - First round to nearest 0.5
    - If within 0.15 of an integer, snap to that integer
    - If snapped integer is odd and time signature suggests 4 beats, bias to nearest even (2 or 4)
    """
    v = max(1.0, min(float(beat_in_bar), float(num)))
    v05 = round(v * 2.0) / 2.0
    # near-integer snap window
    if abs(v05 - round(v05)) <= 0.15:
        v05 = float(round(v05))
        if num == 4:
            iv = int(v05)
            if iv == 3:
                # Bias 3 toward nearest even (2 or 4)
                up = min(num, iv + 1)
                down = max(1, iv - 1)
                v05 = float(up if up % 2 == 0 else down)
    # one decimal place
    return round(v05, 1)

def _detect_qoffset_for_downbeat(
    segs: List[Dict[str, Any]],
    lyrics_lines: List[Dict[str, Any]],
    qbpm: float,
    qpb: float,
) -> float:
    """Estimate a qbeats offset so that bar 1 starts at the first musical event.
    Heuristic:
    - Take earliest timestamp from chord starts or lyric lines.
    - If within ~0.25s of 0 or already near beat 1, use zero offset.
    - Else shift origin so that earliest event lands on bar boundary (beat 1).
    """
    # Collect event times: prioritize chord starts, then lyric lines
    candidates: List[float] = []
    for s in segs:
        try:
            candidates.append(float(s.get("start_sec", 0.0)))
        except Exception:
            pass
    if not candidates:
        for ln in lyrics_lines or []:
            ts = ln.get("ts_sec")
            if isinstance(ts, (int, float)):
                candidates.append(float(ts))
    if not candidates:
        return 0.0
    t0 = max(0.0, min(candidates))
    # If very near zero, don't offset
    if t0 <= 0.25:
        return 0.0
    start_q = _sec_to_qbeats(t0, qbpm)
    # Compute beat-in-bar for t0
    if qpb <= 0:
        return 0.0
    rem = start_q % qpb
    beat_in_bar = (rem % qpb) + 1.0
    # If already close to downbeat, skip
    if abs(beat_in_bar - 1.0) <= 0.3:
        return 0.0
    # Offset so that t0 becomes bar boundary
    return rem


def merge_jcrd_with_lyrics(
    jcrd: Dict[str, Any],
    lyrics_lines: List[Dict[str, Any]],
    *,
    bar_start: str = "auto",  # "auto" or "zero"
    instrumental_min_bars: float = 1.0,
) -> Dict[str, Any]:
    meta = jcrd.get("metadata") or {}
    tempo = meta.get("tempo") or meta.get("bpm")
    time_sig = meta.get("time_signature")
    num, den = _parse_time_signature(str(time_sig) if time_sig else None)
    qbpm = _qbpm_from_tempo_and_ts(tempo, den)
    qpb = _quarter_beats_per_bar(num, den)

    segs = _collect_chord_segments(jcrd)
    last_end = max([s["end_sec"] for s in segs], default=0.0)

    qoffset = 0.0
    if bar_start != "zero":
        qoffset = _detect_qoffset_for_downbeat(segs, lyrics_lines, qbpm, qpb)

    def find_chord(ts: float) -> Optional[str]:
        # Binary search could be used; linear is fine for dev scale
        for s in segs:
            if s["start_sec"] <= ts < s["end_sec"]:
                return s.get("chord")
        # if after last segment, take last chord
        if segs and ts >= segs[-1]["start_sec"]:
            return segs[-1].get("chord")
        return None

    combined_lines: List[Dict[str, Any]] = []
    # Precompute next lyric times
    lyric_ts: List[Optional[float]] = [
        (float(ln.get("ts_sec")) if isinstance(ln.get("ts_sec"), (int, float)) else None)
        for ln in (lyrics_lines or [])
    ]
    n_lyrics = len(lyrics_lines or [])
    for idx, ln in enumerate(lyrics_lines or []):
        text = str(ln.get("text") or "").strip()
        if not text:
            continue
        tsf = lyric_ts[idx]
        next_ts = None
        # find next timed lyric as window end
        for j in range(idx + 1, len(lyric_ts)):
            if isinstance(lyric_ts[j], float):
                next_ts = lyric_ts[j]
                break
        # If untimed lyrics, distribute pseudo timestamps across song duration
        pseudo_used = False
        if tsf is None:
            if last_end and n_lyrics > 1:
                # spread from 0..last_end across lines
                frac = idx / float(max(1, n_lyrics - 1))
                tsf = float(last_end) * frac
            else:
                tsf = 0.0
            pseudo_used = True
            # if next lyric also untimed, estimate next pseudo ts for windowing
            if next_ts is None:
                for j in range(idx + 1, len(lyric_ts)):
                    if lyric_ts[j] is None:
                        if last_end and n_lyrics > 1:
                            frac2 = j / float(max(1, n_lyrics - 1))
                            next_ts = float(last_end) * frac2
                        else:
                            next_ts = last_end
                        break
        if tsf is not None:
            window_start = tsf
            window_end = float(next_ts) if isinstance(next_ts, float) else last_end
            # collect chords overlapping window
            chords_for_line: List[Dict[str, Any]] = []
            for s in segs:
                if s["end_sec"] <= window_start or s["start_sec"] >= window_end:
                    continue
                q = _sec_to_qbeats(s["start_sec"], qbpm)
                q_adj = max(0.0, q - qoffset)
                pos = _format_pos(q_adj, qpb)
                beat_snapped = _snap_beat_one_decimal(float(pos["beat_in_bar"]), num)
                chords_for_line.append({
                    "chord": s.get("chord"),
                    "bar": pos["bar"],
                    "beat_in_bar": beat_snapped,
                })
            # Also include a chord right at the lyric timestamp if nothing matched
            if not chords_for_line:
                q = _sec_to_qbeats(tsf, qbpm)
                q_adj = max(0.0, q - qoffset)
                pos = _format_pos(q_adj, qpb)
                beat_snapped = _snap_beat_one_decimal(float(pos["beat_in_bar"]), num)
                chords_for_line.append({
                    "chord": find_chord(tsf),
                    "bar": pos["bar"],
                    "beat_in_bar": beat_snapped,
                })
            # Lyric position info
            ql = _sec_to_qbeats(tsf, qbpm)
            ql_adj = max(0.0, ql - qoffset)
            posl = _format_pos(ql_adj, qpb)
            combined_lines.append({
                "ts_sec": round(tsf, 3),
                "bar": posl["bar"],
                "beat_in_bar": _snap_beat_one_decimal(float(posl["beat_in_bar"]), num),
                "qbeats": round(ql_adj, 3),
                "text": text,
                "chords": chords_for_line,
            })
        else:
            # should not happen post pseudo placement; keep safe fallback
            combined_lines.append({
                "ts_sec": None,
                "bar": None,
                "beat_in_bar": None,
                "qbeats": None,
                "text": text,
                "chords": [],
            })

    # Insert instrumental lines for music-only segments (no words)
    try:
        # derive lyric timestamps list (only numeric)
        lyric_times = [float(t) for t in lyric_ts if isinstance(t, float)]
        lyric_times.sort()
        sec_per_q = 60.0 / qbpm if qbpm > 0 else 0.5
        sec_per_bar = sec_per_q * qpb if qpb > 0 else 2.0
        # Only emit instrumental lines for spans at least this many bars long
        min_bars = instrumental_min_bars if isinstance(instrumental_min_bars, (int, float)) else 1.0
        gap_threshold = max(0.5, float(min_bars) * sec_per_bar)

        def add_instrumental_segment(seg_start: float, seg_end: float):
            if seg_end - seg_start < gap_threshold:
                return
            # Trim very close to lyric edges to avoid accidental tie-in (small epsilon)
            eps = 0.05
            seg_start += eps
            seg_end -= eps
            if seg_end <= seg_start:
                return
            # collect overlapping chords
            chords_for_line: List[Dict[str, Any]] = []
            for s in segs:
                if s["end_sec"] <= seg_start or s["start_sec"] >= seg_end:
                    continue
                q = _sec_to_qbeats(s["start_sec"], qbpm)
                q_adj = max(0.0, q - qoffset)
                pos = _format_pos(q_adj, qpb)
                beat_snapped = _snap_beat_one_decimal(float(pos["beat_in_bar"]), num)
                chords_for_line.append({
                    "chord": s.get("chord"),
                    "bar": pos["bar"],
                    "beat_in_bar": beat_snapped,
                })
            if not chords_for_line:
                return
            # choose line timestamp at first chord inside segment
            first_chord_time = None
            for s in segs:
                if s["end_sec"] <= seg_start or s["start_sec"] >= seg_end:
                    continue
                first_chord_time = max(seg_start, s["start_sec"])
                break
            tsf = first_chord_time if first_chord_time is not None else seg_start
            ql = _sec_to_qbeats(tsf, qbpm)
            ql_adj = max(0.0, ql - qoffset)
            posl = _format_pos(ql_adj, qpb)
            combined_lines.append({
                "ts_sec": round(tsf, 3),
                "bar": posl["bar"],
                "beat_in_bar": _snap_beat_one_decimal(float(posl["beat_in_bar"]), num),
                "qbeats": round(ql_adj, 3),
                "text": "(instrumental)",
                "chords": chords_for_line,
            })

        if segs:
            # lead-in before first lyric
            first_ts = lyric_times[0] if lyric_times else None
            if isinstance(first_ts, float):
                add_instrumental_segment(0.0, first_ts)
            # no instrumental between lyrics: chords in these spans are tied to adjacent lyric lines
            # tail after last lyric
            if isinstance(first_ts, float) and lyric_times:
                last_ts = lyric_times[-1]
                add_instrumental_segment(last_ts, last_end)
            elif not lyric_times:
                # No lyrics at all: one instrumental covering full song
                add_instrumental_segment(0.0, last_end)
    except Exception:
        pass

    # Sort combined lines by time/bar for stable output
    try:
        combined_lines.sort(key=lambda cl: (
            (cl.get("ts_sec") if isinstance(cl.get("ts_sec"), float) else 1e12),
            (cl.get("bar") if isinstance(cl.get("bar"), int) else 1e9),
            (cl.get("beat_in_bar") if isinstance(cl.get("beat_in_bar"), float) else 1e6),
        ))
    except Exception:
        pass

    # Build a master content text
    content_lines: List[str] = []
    # Default: simple group markers and chord names over lyrics (No Reply-style)
    group_size = max(1, num)
    last_group_start: Optional[int] = None
    for cl in combined_lines:
        # Emit group marker when entering a new group (based on bar)
        if isinstance(cl.get("bar"), int):
            b = int(cl["bar"])
            group_start = ((b - 1) // group_size) * group_size + 1
            if group_start != last_group_start:
                if last_group_start is not None:
                    content_lines.append("")
                content_lines.append(str(group_start))
                last_group_start = group_start
        # Build chord header for the line (names only)
        header_parts: List[str] = []
        for c in cl.get("chords", []) or []:
            if not c.get("chord"):
                continue
            header_parts.append(str(c["chord"]))
        if header_parts:
            content_lines.append("  ".join(header_parts))
        # Then the lyric or instrumental line itself
        if isinstance(cl.get("ts_sec"), float) and isinstance(cl.get("bar"), int) and isinstance(
            cl.get("beat_in_bar"), float
        ):
            # Output lyrics text only (no bar/beat/timestamps)
            content_lines.append(cl["text"])
        else:
            content_lines.append(cl["text"])

    # Replace any [ .. ] tokens with '-'
    content_lines = [re.sub(r"\[[^\]]*\]", "-", ln) for ln in content_lines]
    return {
        "metadata": {
            **meta,
            "time_signature": f"{num}/{den}",
            "bpm": float(tempo) if tempo else 120.0,
            "qbpm": round(qbpm, 4),
            "quarter_beats_per_bar": round(qpb, 4),
            "bar_start": bar_start,
            "qoffset": round(qoffset, 4),
        },
        "lines": combined_lines,
        "content": "\n".join(content_lines),
    }


def chords_only_text(jcrd: Dict[str, Any], *, bar_start: str = "auto") -> Dict[str, Any]:
    """Produce a simple chords-only text from JCRD data with bar/beat positions.
    Returns metadata, a flat chords list, and content string.
    """
    meta = jcrd.get("metadata") or {}
    tempo = meta.get("tempo") or meta.get("bpm")
    time_sig = meta.get("time_signature")
    num, den = _parse_time_signature(str(time_sig) if time_sig else None)
    qbpm = _qbpm_from_tempo_and_ts(tempo, den)
    qpb = _quarter_beats_per_bar(num, den)

    segs = _collect_chord_segments(jcrd)
    qoffset = 0.0
    if bar_start != "zero":
        qoffset = _detect_qoffset_for_downbeat(segs, [], qbpm, qpb)
    chord_rows: List[Dict[str, Any]] = []
    content_lines: List[str] = []
    # Simple group markers and chord lines (No Reply-style)
    last_group_start: Optional[int] = None
    for s in segs:
        q = _sec_to_qbeats(float(s.get("start_sec", 0.0)), qbpm)
        q_adj = max(0.0, q - qoffset)
        pos = _format_pos(q_adj, qpb)
        beat_snapped = _snap_beat_one_decimal(float(pos["beat_in_bar"]), num)
        row = {
            "chord": s.get("chord"),
            "bar": pos["bar"],
            "beat_in_bar": beat_snapped,
        }
        chord_rows.append(row)
        if s.get("chord"):
            # Group marker
            b = int(pos["bar"])
            group_start = ((b - 1) // max(1, num)) * max(1, num) + 1
            if group_start != last_group_start:
                if last_group_start is not None:
                    content_lines.append("")
                content_lines.append(str(group_start))
                last_group_start = group_start
            # Chord name only on its own line
            content_lines.append(f"{s['chord']}")

    # Replace any [ .. ] tokens with '-'
    content_lines = [re.sub(r"\[[^\]]*\]", "-", ln) for ln in content_lines]
    return {
        "metadata": {
            **meta,
            "time_signature": f"{num}/{den}",
            "bpm": float(tempo) if tempo else 120.0,
            "qbpm": round(qbpm, 4),
            "quarter_beats_per_bar": round(qpb, 4),
            "bar_start": bar_start,
            "qoffset": round(qoffset, 4),
        },
        "chords": chord_rows,
        "content": "\n".join(content_lines),
    }
