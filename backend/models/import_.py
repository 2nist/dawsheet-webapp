from pydantic import BaseModel
from typing import List, Optional, Dict

class ImportLayers(BaseModel):
    lyrics: bool = False
    sections: bool = False
    keymode: bool = False
    drums: bool = False

class ImportApply(BaseModel):
    sections: List[Dict] = []
    lyrics: List[Dict] = []
    drums: List[Dict] = []

class ImportRequest(BaseModel):
    project_id: str
    sheet_id: str
    tab: str = "Timeline"
    layers: ImportLayers
    apply: Optional[ImportApply] = None
