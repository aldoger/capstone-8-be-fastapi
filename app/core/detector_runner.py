import threading
import cv2
import time
import os
import numpy as np
from uuid import UUID
from config import Config
from app.core.frame_manager import FrameManager
from app.core.model import ONNXRuntime
from app.core.tracker import Tracker


class DetectorRunner:
    """Runs object detection in a background thread, integrated with FastAPI.

    Each runner owns its own FrameManager and operates on a single camera source.
    """

    def __init__(self, id: UUID, type_source: str, url: str | None, model_name: str = "rfdetr"):
        self.id = id
        self.type_source = type_source
        self.url = url
        self.model_name = model_name
        self._thread: threading.Thread | None = None
        self._running = False
        self._model: ONNXRuntime | None = None
        self._tracker: Tracker | None = None
        self._frame_manager = FrameManager()

    def start(self, on_detection_callback, on_snapshot_callback):
        """Start detection loop in a daemon background thread.

        Args:
            on_detection_callback: fn(source_id: UUID, head_count: int, fps: float) called every interval.
            on_snapshot_callback: fn(source_id: UUID, head_count: int, frame: np.ndarray) called every interval.
        """
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop,
            args=(on_detection_callback, on_snapshot_callback),
            daemon=True,
        )
        self._thread.start()
        print(f"[DETECTOR {self.id}] Started with model: {self.model_name}")

    def stop(self):
        """Signal the detection loop to stop and wait for the thread to finish."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            alive = self._thread.is_alive()
            if alive:
                print(f"[DETECTOR {self.id}] Stop timed out — thread still running")
            else:
                print(f"[DETECTOR {self.id}] Stopped")
            return not alive  # True = stopped clean, False = timeout
        return True

    def get_jpeg(self) -> bytes | None:
        """Get the latest JPEG frame from this runner's FrameManager."""
        return self._frame_manager.get_jpeg()

    def get_frame(self) -> np.ndarray | None:
        """Get the latest raw numpy frame from this runner's FrameManager."""
        return self._frame_manager.get_frame()

    def _load_model(self):
        """Load the ONNX model and tracker (runs inside the background thread)."""
        print(f"[DETECTOR {self.id}] Loading model: {self.model_name}...")
        self._model = ONNXRuntime(
            model_path=Config.MODEL_PATH,
            inference_size=Config.INFERENCE_SIZE,
            conf_threshold=Config.CONFIDENCE_THRESHOLD,
            target_class_ids=Config.TARGET_CLASS_IDS,
        )
        self._tracker = Tracker(
            activate=Config.ACTIVATE_TRACKER,
            tracker=Config.TRACKER,
        )
        print(self._model.session.get_providers())
        print(f"[DETECTOR {self.id}] Model loaded successfully")

    def _run_loop(self, on_detection, on_snapshot):
        """Main detection loop — captures frames, runs inference, updates frame manager."""
        try:
            self._load_model()
        except Exception as e:
            print(f"[DETECTOR {self.id}] Failed to load model: {e}")
            return

        if self.type_source == "RTSP":
            if self.url is None:
                print(f"[DETECTOR {self.id}] RTSP source has no URL, aborting")
                return
            source = self.url
        else:
            if self.url is None:
                print(f"[DETECTOR {self.id}] Source has no URL, aborting")
                return
            source = self.url
            # source = os.getenv("CAMERA_SOURCE", "0")
            # source = int(source) if source.isdigit() else source
            
        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            print(f"[DETECTOR {self.id}] Failed to open camera source: {source}")
            return

        print(f"[DETECTOR {self.id}] Camera opened, starting detection loop")
        last_time = 0
        interval_start = time.time()
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        while self._running:
            ret, frame = cap.read()
            if not ret:
                if not self._running:
                    break
                time.sleep(0.1)
                continue

            current_time = time.time()
            fps = 1 / (current_time - last_time) if last_time > 0 else 0
            last_time = current_time

            # Run inference
            try:
                annotated_frame, head_count = self._detect(frame)
                if not self._running:
                    break
            except Exception as e:
                print(f"[DETECTOR {self.id}] Inference error: {e}")
                continue

            # Update this runner's own frame buffer (thread-safe)
            self._frame_manager.update(annotated_frame)

            # Periodic detection + snapshot callback (every 10s)
            if current_time - interval_start >= 10:
                try:
                    on_detection(self.id, head_count, fps)
                    on_snapshot(self.id, head_count, frame)
                except Exception as e:
                    print(f"[DETECTOR {self.id}] Callback error: {e}")
                interval_start = current_time

        cap.release()
        print(f"[DETECTOR {self.id}] Camera released")

    def _detect(self, frame):
        """Run detection on a single frame. Returns (annotated_frame, head_count)."""
        h, w = frame.shape[:2]
        detections = self._model.predict(frame, display_size=(w, h))
        annotated_frame = self._tracker.track_and_draw(frame, detections)
        head_count = len(detections)
        return annotated_frame, head_count
