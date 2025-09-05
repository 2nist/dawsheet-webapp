from pydantic import BaseModel

class ExportRequest(BaseModel):
    project_id: str
