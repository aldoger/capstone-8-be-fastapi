from app.schemas.detection_schema import HeadDetection

class AggregationService:

    def __init__(self):
        self.buffer: HeadDetection | None = None

    def add_detection(self, detection: HeadDetection):

        self.buffer =  detection

        return None

    def get_detection_data(self):
        return self.buffer


aggregator = AggregationService()