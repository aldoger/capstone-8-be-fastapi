import threading
import cv2
import time
import os
import numpy as np
from uuid import UUID

from app.core.frame_manager import FrameManager


class DetectorRunner:
    """Runs object detection in a background thread, integrated with FastAPI.
    
    Each runner owns its own FrameManager and operates on a single camera source.
    """

    def __init__(self, id: UUID, type_source: str, url: str | None, model_name: str = "yolo"):
        self.id = id
        self.type_source = type_source
        self.url = url
        self.model_name = model_name
        self._thread: threading.Thread | None = None
        self._running = False
        self._model = None
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
            print(f"[DETECTOR {self.id}] Stopped")

    def get_jpeg(self) -> bytes | None:
        """Get the latest JPEG frame from this runner's FrameManager."""
        return self._frame_manager.get_jpeg()

    def get_frame(self) -> np.ndarray | None:
        """Get the latest raw numpy frame from this runner's FrameManager."""
        return self._frame_manager.get_frame()

    def _load_model(self):
        """Load the AI model (runs inside the background thread)."""
        print(f"[DETECTOR {self.id}] Loading model: {self.model_name}...")
        if self.model_name == "yolo":
            from ultralytics import YOLO

            self._model = YOLO("yolo.pt")
        else:
            from rfdetr import RFDETRNano

            self._model = RFDETRNano(pretrain_weights="checkpoint_best_total.pth")
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
        if self.model_name == "yolo":
            result = self._model.track(frame, persist=True)
            annotated = result[0].plot()
            boxes = result[0].boxes
            count = (
                int((boxes.cls == 1).sum())
                if boxes is not None and boxes.cls is not None
                else 0
            )
            return annotated, count
        else:
            import supervision as sv
            from rfdetr.assets.coco_classes import COCO_CLASSES

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            detections = self._model.predict(frame_rgb, threshold=0.5)
            count = sum(1 for c in detections.class_id if c == 1)
            labels = [COCO_CLASSES[cid] for cid in detections.class_id]

            box_ann = sv.BoxAnnotator()
            label_ann = sv.LabelAnnotator()
            annotated = box_ann.annotate(frame_rgb, detections)
            annotated = label_ann.annotate(annotated, detections, labels)
            return annotated, count