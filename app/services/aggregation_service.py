from app.schemas.detection_schema import HeadDetection
import requests
import os

class AggregationService:

    def __init__(self):
        self.buffer: HeadDetection | None = None
        self.core_url = os.getenv("BE_CORE_URL")

    def add_detection(self, detection: HeadDetection):

        self.buffer =  detection

        self.send_detection()

        return None

    def get_detection_data(self):
        return self.buffer
    
    def send_detection(self):
        try:
            requests.post(self.core_url, self.buffer)
        except Exception as e:
            print("Error sending data:", e)





aggregator = AggregationService()