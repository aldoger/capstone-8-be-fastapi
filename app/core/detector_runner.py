import threading
import cv2
import time
import os
import numpy as np
from uuid import UUID
import httpx

from app.core.frame_manager import FrameManager


class DetectorRunner:
    def __init__(self, id: UUID, type_source: str, url: str | None):
        self.id = id
        self.type_source = type_source
        self.url = url
        self._thread: threading.Thread | None = None
        self._running = False
        self.model_url = os.getenv("BE_MODEL_URL")
        self._frame_manager = FrameManager()

    def start(self, on_detection_callback, on_snapshot_callback):
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop,
            args=(on_detection_callback, on_snapshot_callback),
            daemon=True,
        )
        self._thread.start()
        print(f"[DETECTOR {self.id}] Started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            print(f"[DETECTOR {self.id}] Stopped")

    def get_jpeg(self) -> bytes | None:
        return self._frame_manager.get_jpeg()

    def get_frame(self) -> np.ndarray | None:
        return self._frame_manager.get_frame()

    def _run_loop(self, on_detection, on_snapshot):
        if self.type_source == "RTSP":
            if self.url is None:
                print(f"[DETECTOR {self.id}] RTSP source has no URL, aborting")
                return
            source = self.url
        else:
            source = os.getenv("CAMERA_SOURCE", "0")
            source = int(source) if source.isdigit() else source

        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            print(f"[DETECTOR {self.id}] Failed to open camera source: {source}")
            return

        print(f"[DETECTOR {self.id}] Camera opened, starting detection loop")
        last_time = 0
        interval_start = time.time()

        while self._running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            current_time = time.time()
            fps = 1 / (current_time - last_time) if last_time > 0 else 0
            last_time = current_time

            # Run inference
            try:
                annotated_frame, head_count = self._detect(frame)
            except Exception as e:
                print(f"[DETECTOR {self.id}] Inference error: {e}")
                continue

            self._frame_manager.update(annotated_frame)

            if current_time - interval_start >= 10:
                try:
                    on_detection(self.id, head_count, fps)
                    on_snapshot(self.id, head_count, frame)
                except Exception as e:
                    print(f"[DETECTOR {self.id}] Callback error: {e}")
                interval_start = current_time

        cap.release()
        print(f"[DETECTOR {self.id}] Camera released")

    def _detect(self, frame: np.ndarray) -> tuple[np.ndarray, int]:
        """Send frame to Vast.ai model, return (annotated_frame, head_count)."""
        _, encoded = cv2.imencode(".jpg", frame)
        jpg_bytes = encoded.tobytes()

        with httpx.Client() as client:
            response = client.post(
                self.model_url,
                files={"file": ("frame.jpg", jpg_bytes, "image/jpeg")},
            )
            response.raise_for_status()

        data = response.json()

        # Decode annotated image from response
        annotated_bytes = np.frombuffer(data["annotated_image"], dtype=np.uint8)
        annotated_frame = cv2.imdecode(annotated_bytes, cv2.IMREAD_COLOR)

        head_count = data["count"]

        return annotated_frame, head_count