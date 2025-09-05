from typing import List, Dict, Any
from google.oauth2.service_account import Credentials as SACredentials
from googleapiclient.discovery import build

TIMELINE_COLS = [
    "Bar","Beat","BeatAbs","Time_s","Timecode","Chord","Section","Dur_beats","Dur_s",
    "Lyric","Lyric_conf","EventType","WordStart_s","WordEnd_s","SubIdx","Melisma",
    "Chord_conf","Section_conf","Source","ProjectId","EventId"
]

GUIDEDRUMS_COLS = [
    "Bar","Beat","Sixteenth","Pitch","Velocity","Dur_s","Source","ProjectId","EventId"
]

SECTIONS_COLS = [
    "Name","BarStart","Bars","Style","Conf","SectionId","ProjectId","Chords","LyricsRef","Notes","EventId"
]

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _svc(service_account_path: str):
    creds = SACredentials.from_service_account_file(service_account_path, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def _ensure_tab(svc, sheet_id: str, tab: str):
    meta = svc.spreadsheets().get(spreadsheetId=sheet_id).execute()
    for s in meta.get("sheets", []):
        if s.get("properties", {}).get("title") == tab:
            return
    svc.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={
        "requests":[{"addSheet":{"properties":{"title": tab}}}]
    }).execute()


def _write_headers_if_empty(svc, sheet_id: str, tab: str, headers: List[str]):
    rng = f"{tab}!1:1"
    resp = svc.spreadsheets().values().get(spreadsheetId=sheet_id, range=rng).execute()
    if not resp.get("values"):
        svc.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"{tab}!A1",
            valueInputOption="RAW",
            body={"values":[headers]},
        ).execute()


def _append_values(svc, sheet_id: str, tab: str, values: List[List[Any]]):
    if not values:
        return 0
    svc.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range=f"{tab}!A:A",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": values},
    ).execute()
    return len(values)


def append_timeline_rows(sheet_id: str, rows: List[Dict[str,Any]], service_account_path: str) -> int:
    svc = _svc(service_account_path)
    tab = "Timeline"
    _ensure_tab(svc, sheet_id, tab)
    _write_headers_if_empty(svc, sheet_id, tab, TIMELINE_COLS)
    values = [[r.get(c, "") for c in TIMELINE_COLS] for r in rows]
    return _append_values(svc, sheet_id, tab, values)


def append_guidedrums_rows(sheet_id: str, rows: List[Dict[str,Any]], service_account_path: str) -> int:
    svc = _svc(service_account_path)
    tab = "GuideDrums"
    _ensure_tab(svc, sheet_id, tab)
    _write_headers_if_empty(svc, sheet_id, tab, GUIDEDRUMS_COLS)
    values = [[r.get(c, "") for c in GUIDEDRUMS_COLS] for r in rows]
    return _append_values(svc, sheet_id, tab, values)


def upsert_metadata(sheet_id: str, kv: Dict[str, Any], service_account_path: str) -> None:
    svc = _svc(service_account_path)
    tab = "Metadata"
    _ensure_tab(svc, sheet_id, tab)
    # ensure headers
    resp = svc.spreadsheets().values().get(spreadsheetId=sheet_id, range=f"{tab}!1:1").execute()
    if not resp.get("values"):
        svc.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"{tab}!A1",
            valueInputOption="RAW",
            body={"values":[["Key","Value"]]},
        ).execute()


def append_sections_rows(sheet_id: str, rows: List[Dict[str, Any]], service_account_path: str) -> int:
    """Append Section rows to a 'Sections' tab with canonical columns.
    Columns: Name, BarStart, Bars, Conf, Style, ProjectId, EventId
    """
    if not rows:
        # Ensure the tab and headers exist even if no rows yet
        svc = _svc(service_account_path)
        tab = "Sections"
        _ensure_tab(svc, sheet_id, tab)
        _write_headers_if_empty(svc, sheet_id, tab, SECTIONS_COLS)
        return 0
    svc = _svc(service_account_path)
    tab = "Sections"
    _ensure_tab(svc, sheet_id, tab)
    _write_headers_if_empty(svc, sheet_id, tab, SECTIONS_COLS)
    values = [[r.get(c, "") for c in SECTIONS_COLS] for r in rows]
    return _append_values(svc, sheet_id, tab, values)

    # read existing
    resp = svc.spreadsheets().values().get(spreadsheetId=sheet_id, range=f"{tab}!A2:B").execute()
    rows = resp.get("values", [])
    idx = { (r[0] if r else ""): i for i, r in enumerate(rows) if r }

    updates = []
    appends = []
    for k, v in kv.items():
        if k in idx:
            r = idx[k] + 2
            updates.append({"range": f"{tab}!A{r}:B{r}", "values": [[k, str(v)]]})
        else:
            appends.append([k, str(v)])

    if updates:
        svc.spreadsheets().values().batchUpdate(
            spreadsheetId=sheet_id,
            body={"valueInputOption":"RAW","data": updates}
        ).execute()
    if appends:
        svc.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=f"{tab}!A:B",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": appends}
        ).execute()
