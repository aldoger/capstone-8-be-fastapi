from typing import List
from app.schemas.detection_schema import HeadDetection

class AggregationService:

    def __init__(self):
        self.buffer: List[HeadDetection] = []
        self.max_buffer_size = 10

    def add_detection(self, detections: List[HeadDetection]):

        self.buffer.extend(detections)

        if len(self.buffer) >= self.max_buffer_size:
            return self.flush()

        return None

    def get_buffer_size(self):
        return len(self.buffer)

    def get_detection_data(self):
        return self.buffer

    def flush(self):
        data = self.buffer
        self.buffer = []
        return data


aggregator = AggregationService()