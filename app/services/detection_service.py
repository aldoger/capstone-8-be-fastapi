from app.schemas.detection_schema import DetectionResult, SnapshotData
from app.schemas.source_schema import SourceData
from app.utils.http_client import send_batch, send_snapshot
import os

class DetectionService:

    def __init__(self):
        self.buffer: DetectionResult | None = None
        self.snapshot_data: SnapshotData | None = None
        self.source_map: dict[str, str] = {}
        self.core_url = os.getenv("BE_CORE_URL")

    def build_source_map(self, sources: list[SourceData]):
        seen = set()
        self.source_map = {}

        for src in sources:
            key = src.type.lower().replace(" ", "")

            if key in seen:
                raise ValueError(f"Duplicate source type: {src.type}")

            seen.add(key)
            self.source_map[key] = str(src.id)

    def find_source_id(self, source_type: str) -> str | None:
        key = source_type.lower().replace(" ", "")
        return self.source_map.get(key)

    def send_head_detection(self, data: DetectionResult, type_source: str):

        source_id = self.find_source_id(type_source)

        self.buffer =  data

        try:
            payload = self.buffer.model_dump(mode="json")
            payload["source_id"] = source_id
            send_batch(f"{self.core_url}/logs", payload=payload)
        except Exception as e:
            print("Error sending payload: ", e)
    
    def send_snapshot_data(self, data: SnapshotData, type_source: str, filename, frame):

        source_id = self.find_source_id(type_source)

        self.snapshot_data = data

        try:
            payload = self.snapshot_data.model_dump(mode="json")
            payload["source_id"] = source_id
            send_snapshot(f"{self.core_url}/snapshots", payload, filename, frame)
        except Exception as e:
            print("Error sending payload: ", e)

        payload = self.snapshot_data.model_dump(mode="json")
        send_snapshot(f"{self.core_url}/snapshots", payload, filename, frame)


detection_service = DetectionService()