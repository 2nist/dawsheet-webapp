from fastapi import APIRouter

router = APIRouter()

@router.get("")
def list_songs():
    # TODO: read from Index sheet or SQLite
    return {"songs": []}

@router.get("/{project_id}")
def get_song(project_id: str):
    return {"project_id": project_id, "sheet_id": None}
