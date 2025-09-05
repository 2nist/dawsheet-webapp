from typing import List, Dict, Any
from google.oauth2.service_account import Credentials as SACredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def _svc(service_account_path: str):
    creds = SACredentials.from_service_account_file(service_account_path, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


ession = None

def read_rows(sheet_id: str, tab: str, service_account_path: str) -> List[Dict[str, Any]]:
    svc = _svc(service_account_path)
    rng = f"{tab}!A1:Z"
    try:
        resp = svc.spreadsheets().values().get(spreadsheetId=sheet_id, range=rng).execute()
    except HttpError:
        # Tab might not exist or range invalid → treat as empty
        return []
    values = resp.get("values", [])
    if not values:
        return []
    headers = values[0]
    out = []
    for row in values[1:]:
        padded = row + [""] * (len(headers) - len(row))
        out.append(dict(zip(headers, padded)))
    return out


def read_timeline(sheet_id: str, service_account_path: str) -> List[Dict[str, Any]]:
    return read_rows(sheet_id, "Timeline", service_account_path)


def read_guidedrums(sheet_id: str, service_account_path: str) -> List[Dict[str, Any]]:
    return read_rows(sheet_id, "GuideDrums", service_account_path)


def read_metadata(sheet_id: str, service_account_path: str) -> Dict[str, Any]:
    rows = read_rows(sheet_id, "Metadata", service_account_path)
    meta = {}
    for r in rows:
        k = (r.get("Key") or "").strip()
        v = r.get("Value")
        if k:
            meta[k] = v
    return meta


def read_sections(sheet_id: str, service_account_path: str) -> List[Dict[str, Any]]:
    return read_rows(sheet_id, "Sections", service_account_path)
