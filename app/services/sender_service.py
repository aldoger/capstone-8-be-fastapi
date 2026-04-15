from datetime import datetime
from uuid import UUID
from app.utils.http_client import send_batch, send_snapshot
import os


class SenderService:

    def __init__(self):
        self.core_url = os.getenv("BE_CORE_URL")

    # --- Direct callbacks (called from detector thread, no HTTP self-call) ---

    def handle_detection(self, source_id: UUID, head_count: int, fps: float):
        """Called directly by detector thread to send detection data to BE Core."""
        payload = {
            "head_count": head_count,
            "current_fps": fps,
            "timestamp": datetime.now().isoformat(),
            "source_id": str(source_id),
        }

        try:
            send_batch(f"{self.core_url}/logs", payload=payload)
        except Exception as e:
            print(f"[DETECTION] Error sending to BE Core: {e}")

    def handle_snapshot(self, source_id: UUID, head_count: int, frame):
        """Called directly by detector thread to send snapshot to BE Core."""
        filename = f'snapshots/photo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        payload = {
            "head_count_at_time": head_count,
            "image_path": filename,
            "source_id": str(source_id),
        }

        try:
            send_snapshot(f"{self.core_url}/snapshots", payload, filename, frame)
        except Exception as e:
            print(f"[SNAPSHOT] Error sending to BE Core: {e}")


sender_service = SenderService()