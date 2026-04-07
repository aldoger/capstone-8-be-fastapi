from pydantic import BaseModel
from datetime import datetime

class DetectionResult(BaseModel):
    head_count: int
    current_fps: str
    timestamp: datetime

class SnapshotData(BaseModel):
    id: int
    source_id: str
    image_path: str
    head_count_at_time: int
