from app.schemas.detection_schema import HeadDetection
from app.utils.http_client import send_batch
import os

class AggregationService:

    def __init__(self):
        self.buffer: HeadDetection | None = None
        self.core_url = os.getenv("BE_CORE_URL")

    def add_detection(self, detection: HeadDetection):

        self.buffer =  detection

        try:
            payload = self.buffer.model_dump(mode="json")
            send_batch(f"{self.core_url}/logs", payload=payload)
        except Exception as e:
            print("Error sending payload: ", e)

        return None

    def get_detection_data(self):
        return self.buffer


aggregator = AggregationService()