from pydantic import BaseModel
from datetime import datetime

class DetectionResult(BaseModel):
    head_count: int
    current_fps: str
    timestamp: datetime