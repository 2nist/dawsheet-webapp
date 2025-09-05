from fastapi import APIRouter
from ..models.analyze import AnalyzeRequest, AnalyzePreview

router = APIRouter()

@router.post("")
def run_analyze(req: AnalyzeRequest):
    # TODO: dispatch job; for now return fake job id
    return {"job_id": "job-123"}

@router.get("/{job_id}/preview")
def get_preview(job_id: str) -> AnalyzePreview:
    # TODO: return real preview
    return AnalyzePreview(
        summary={"duration_s":0,"bpm_est":0,"key":None,"mode":None,"ts":"4/4"},
        sections=[], lyrics=[], drums={}, diagnostics={}
    )
