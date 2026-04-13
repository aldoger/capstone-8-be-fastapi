from datetime import datetime
from app.schemas.detection_schema import DetectionResult, SnapshotData
from app.schemas.source_schema import SourceData
from app.utils.http_client import send_batch, send_snapshot
import os


class DetectionService:

    def __init__(self):
        self.source_map: dict[str, str] = {}
        self.core_url = os.getenv("BE_CORE_URL")

    def add_source(self, source: SourceData) -> bool:
        seen_source = self.find_source_id(source_name=source.name)
        if seen_source is not None:
            return False

        key = source.name.lower().replace(" ", "")
        self.source_map[key] = str(source.id)
        return True

    def build_source_map(self, sources: list[SourceData]):
        seen = set()
        self.source_map = {}

        for src in sources:
            key = src.name.lower().replace(" ", "")

            if key in seen:
                raise ValueError(f"Duplicate source name: {src.name}")

            seen.add(key)
            self.source_map[key] = str(src.id)

    def find_source_id(self, source_name: str) -> str | None:
        key = source_name.lower().replace(" ", "")
        return self.source_map.get(key)

    # --- HTTP endpoint handlers (called from routers) ---

    def send_head_detection(self, data: DetectionResult, source_name: str):
        source_id = self.find_source_id(source_name)

        try:
            payload = data.model_dump(mode="json")
            payload["source_id"] = source_id
            send_batch(f"{self.core_url}/logs", payload=payload)
        except Exception as e:
            print("Error sending detection payload: ", e)

    def send_snapshot_data(self, data: SnapshotData, source_name: str, filename, frame):
        source_id = self.find_source_id(source_name)

        try:
            payload = data.model_dump(mode="json")
            payload["source_id"] = source_id
            send_snapshot(f"{self.core_url}/snapshots", payload, filename, frame)
        except Exception as e:
            print("Error sending snapshot payload: ", e)

    # --- Direct callbacks (called from detector thread, no HTTP self-call) ---

    def handle_detection(self, head_count: int, fps: float, source_name: str = "webcam"):
        """Called directly by detector thread to send detection data to BE Core."""
        source_id = self.find_source_id(source_name)

        payload = {
            "head_count": head_count,
            "current_fps": fps,
            "timestamp": datetime.now().isoformat(),
            "source_id": source_id,
        }

        try:
            send_batch(f"{self.core_url}/logs", payload=payload)
        except Exception as e:
            print(f"[DETECTION] Error sending to BE Core: {e}")

    def handle_snapshot(self, head_count: int, frame, source_name: str = "webcam"):
        """Called directly by detector thread to send snapshot to BE Core."""
        source_id = self.find_source_id(source_name)

        filename = f'snapshots/photo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        payload = {
            "head_count_at_time": head_count,
            "image_path": filename,
            "source_id": source_id,
        }

        try:
            send_snapshot(f"{self.core_url}/snapshots", payload, filename, frame)
        except Exception as e:
            print(f"[SNAPSHOT] Error sending to BE Core: {e}")


detection_service = DetectionService()