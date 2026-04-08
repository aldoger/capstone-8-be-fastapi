from app.schemas.detection_schema import DetectionResult, SnapshotData, SnapshotWithDetection
from app.utils.http_client import send_batch, send_snapshot
import os

class AggregationService:

    def __init__(self):
        self.buffer: DetectionResult | None = None
        self.snapshot_data: SnapshotData | None = None
        self.core_url = os.getenv("BE_CORE_URL")

    def add_detection(self, data: SnapshotWithDetection):

        self.buffer =  data.detection
        self.snapshot_data = data.snapshot

        try:
            self.send_head_detection_data()
        except Exception as e:
            print("Error sending payload: ", e)

        return None
    
    def send_head_detection_data(self):
        payload = self.buffer.model_dump(mode="json")
        send_batch(f"{self.core_url}/logs", payload=payload)


aggregator = AggregationService()