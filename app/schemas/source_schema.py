from pydantic import BaseModel
from uuid import UUID

class SourceData(BaseModel):
    id: UUID
    type: str