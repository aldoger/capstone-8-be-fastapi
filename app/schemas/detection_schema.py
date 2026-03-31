from pydantic import BaseModel
from datetime import datetime

class DetectionResult(BaseModel):
    head_count: int
    fps: str
    timestamp: datetime

class HeadDetection(BaseModel):
    source: str
    model_type: str
    result: DetectionResult