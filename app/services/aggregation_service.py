from typing import List
from app.schemas.detection_schema import Detection

class AggregationService:

    def __init__(self):
        self.buffer: List[Detection] = []

    def add_detection(self, detection: Detection):
        self.buffer.append(detection)

    def get_buffer_size(self):
        return len(self.buffer)

    def get_detection_data(self):
        return self.buffer

    def flush(self):
        data = self.buffer
        self.buffer = []
        return data


aggregator = AggregationService()