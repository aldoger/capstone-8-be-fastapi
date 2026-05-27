from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class DetectionResult(BaseModel):
    head_count: int
    current_fps: float
    timestamp: datetime

class DetectionData(DetectionResult):
    source_id: UUID

class SnapshotData(BaseModel):
    source_id: UUID
    image_path: str
    head_count_at_time: int