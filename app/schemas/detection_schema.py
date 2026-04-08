from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class DetectionResult(BaseModel):
    source_id: UUID
    head_count: int
    current_fps: float
    timestamp: datetime

class SnapshotData(BaseModel):
    source_id: UUID
    image_path: str
    head_count_at_time: int