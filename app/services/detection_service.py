from app.schemas.detection_schema import DetectionResult, SnapshotData
from app.utils.http_client import send_batch, send_snapshot
import os

class DetectionService:

    def __init__(self):
        self.buffer: DetectionResult | None = None
        self.snapshot_data: SnapshotData | None = None
        self.core_url = os.getenv("BE_CORE_URL")

    def send_head_detection(self, data: DetectionResult):

        self.buffer =  data

        try:
            payload = self.buffer.model_dump(mode="json")
            send_batch(f"{self.core_url}/logs", payload=payload)
        except Exception as e:
            print("Error sending payload: ", e)

        return None
    
    def send_snapshot_data(self, data: SnapshotData, filename, frame):

        self.snapshot_data = data

        payload = self.snapshot_data.model_dump(mode="json")
        send_snapshot(f"{self.core_url}/snapshots", payload, filename, frame)


detection_service = DetectionService()