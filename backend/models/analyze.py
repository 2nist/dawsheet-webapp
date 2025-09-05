from pydantic import BaseModel
from typing import List, Optional, Literal, Dict

class AnalyzeOptions(BaseModel):
    snap: Literal["1/4","1/8"] = "1/4"
    section_min_bars: int = 8
    tempo_smoothing: Literal["per_section","none"] = "per_section"
    drums_detect: bool = True
    drums_style_hint: Literal["auto","normal","half","double"] = "auto"
    keymode: bool = True
    lrclib_first: bool = True
    run_asr_if_missing: bool = False

class AnalyzeRequest(BaseModel):
    project_id: str
    sheet_id: Optional[str] = None
    midi_path: Optional[str] = None
    mp3_path: Optional[str] = None
    artist: Optional[str] = None
    title: Optional[str] = None
    ts_num: Optional[int] = 4
    pickup_beats: Optional[float] = 0.0
    tempo_map: Optional[list] = None
    options: AnalyzeOptions = AnalyzeOptions()

class PreviewLyric(BaseModel):
    text: str
    start_s: float
    end_s: Optional[float] = None
    bar: int
    beat: float
    subidx: int = 0
    melisma: bool = False
    conf: float = 0.9
    source: Literal["lrclib","asr","paste"] = "lrclib"

class PreviewSection(BaseModel):
    id: str
    name: str
    bar_start: int
    bars: int
    conf: float = 0.9
    style_hint: Literal["normal","half","double"] = "normal"

class PreviewDrums(BaseModel):
    section_id: str
    style: Literal["normal","half","double"] = "normal"
    grid: list
    fills: list = []

class AnalyzePreview(BaseModel):
    summary: Dict
    sections: List[PreviewSection] = []
    lyrics: List[PreviewLyric] = []
    drums: Dict = {}
    diagnostics: Dict = {}
