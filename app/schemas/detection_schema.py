from pydantic import BaseModel
from datetime import datetime
from typing import List


class Detection(BaseModel):
    id: str
    object: str
    timestamp: datetime


class AggregatedDetection(BaseModel):
    detections: List[Detection]