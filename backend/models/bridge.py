from pydantic import BaseModel
from typing import Optional, Literal

class BridgeConfig(BaseModel):
    midi_port: Optional[str] = None
    osc_host: str = "127.0.0.1"
    osc_port: int = 9000
    export_root: str = "./exports"

class BridgeSend(BaseModel):
    project_id: str
    kind: Literal["drums","section_cues","bar_cues"] = "drums"
    bars: int = 8
