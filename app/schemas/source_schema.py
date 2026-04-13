from pydantic import BaseModel
from uuid import UUID

class SourceData(BaseModel):
    id: UUID
    name: str
    type: str


class ProbeResponse(BaseModel):
    exists: bool
    detail: str