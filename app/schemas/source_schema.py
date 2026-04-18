from pydantic import BaseModel
from uuid import UUID

class SourceData(BaseModel):
    id: UUID
    type: str
    url: str | None = None


class ProbeResponse(BaseModel):
    exists: bool
    detail: str
    url: str
    resolution: str
    fps: int