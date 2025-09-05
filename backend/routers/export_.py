from fastapi import APIRouter, Response, HTTPException, Query
from exports.timeline_json_builder import build_timeline_json
from exports.midi_builder import drums_rows_to_midi
from exports.markers_csv_builder import build_markers_csv_bytes
from webapp.backend.io.sheets_reader import read_timeline, read_guidedrums, read_metadata, read_sections
import io, os

router = APIRouter()

def _require_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise HTTPException(status_code=500, detail=f"Missing env {name}")
    return v

@router.get("/timeline_json")
def timeline_json(project_id: str = Query(...), sheet_id: str = Query(...)):
    sa = _require_env("GOOGLE_SA_JSON")
    tl = read_timeline(sheet_id, sa)
    meta = read_metadata(sheet_id, sa) or {"ts_num":4,"ts_denom":4,"bpm_sections":[{"start_bar":1,"bpm":120.0}]}
    return build_timeline_json(tl, meta)

@router.get("/drums_midi")
def drums_midi(project_id: str = Query(...), sheet_id: str = Query(...)):
    sa = _require_env("GOOGLE_SA_JSON")
    gd = read_guidedrums(sheet_id, sa)
    meta = read_metadata(sheet_id, sa) or {"ts_num":4,"bpm_sections":[{"start_bar":1,"bpm":120.0}]}
    pm = drums_rows_to_midi(gd, meta)
    buf = io.BytesIO(); pm.write(buf); buf.seek(0)
    return Response(content=buf.read(), media_type="audio/midi", headers={
        "Content-Disposition": f'attachment; filename="{project_id}_drums.mid"'
    })

@router.get("/markers_csv")
def markers_csv(project_id: str = Query(...), sheet_id: str = Query(...)):
    sa = _require_env("GOOGLE_SA_JSON")
    meta = read_metadata(sheet_id, sa) or {"ts_num":4,"bpm_sections":[{"start_bar":1,"bpm":120.0}]}
    # Prefer explicit Sections tab; else fallback to naive extraction from Timeline
    sections_tab = read_sections(sheet_id, sa)
    if sections_tab:
        sections = []
        for s in sections_tab:
            try:
                sections.append({
                    "name": s.get("Name", "Section"),
                    "bar_start": int(float(s.get("BarStart") or 1)),
                    "bars": int(float(s.get("Bars") or 0)),
                })
            except Exception:
                continue
    else:
        tl = read_timeline(sheet_id, sa)
        sections = []
        last = None
        for r in tl:
            sec = (r.get("Section") or "").strip()
            if not sec:
                continue
            try:
                bar = int(float(r.get("Bar") or 0) or 0)
            except Exception:
                bar = 0
            if bar <= 0:
                continue
            if last != sec:
                sections.append({"name": sec, "bar_start": bar})
                last = sec
    csv_bytes = build_markers_csv_bytes(sections, meta)
    return Response(content=csv_bytes, media_type="text/csv", headers={
        "Content-Disposition": f'attachment; filename="{project_id}_markers.csv"'
    })
