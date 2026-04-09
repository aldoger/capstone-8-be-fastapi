import threading
import cv2
import time
import os


class DetectorRunner:
    """Runs object detection in a background thread, integrated with FastAPI."""

    def __init__(self, model_name: str = "yolo"):
        self.model_name = model_name
        self._thread: threading.Thread | None = None
        self._running = False
        self._model = None

    def start(self, frame_manager, on_detection_callback, on_snapshot_callback):
        """Start detection loop in a daemon background thread.

        Args:
            frame_manager: FrameManager instance to push annotated frames into.
            on_detection_callback: fn(head_count: int, fps: float) called every interval.
            on_snapshot_callback: fn(head_count: int, frame: np.ndarray) called every interval.
        """
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop,
            args=(frame_manager, on_detection_callback, on_snapshot_callback),
            daemon=True,
        )
        self._thread.start()
        print(f"[DETECTOR] Started with model: {self.model_name}")

    def stop(self):
        """Signal the detection loop to stop and wait for the thread to finish."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            print("[DETECTOR] Stopped")

    def _load_model(self):
        """Load the AI model (runs inside the background thread)."""
        print(f"[DETECTOR] Loading model: {self.model_name}...")
        if self.model_name == "yolo":
            from ultralytics import YOLO

            self._model = YOLO("yolo.pt")
        else:
            from rfdetr import RFDETRNano

            self._model = RFDETRNano(pretrain_weights="checkpoint_best_total.pth")
        print(f"[DETECTOR] Model loaded successfully")

    def _run_loop(self, frame_manager, on_detection, on_snapshot):
        """Main detection loop — captures frames, runs inference, updates frame manager."""
        try:
            self._load_model()
        except Exception as e:
            print(f"[DETECTOR] Failed to load model: {e}")
            return

        source = os.getenv("CAMERA_SOURCE", "0")
        cap = cv2.VideoCapture(int(source) if source.isdigit() else source)

        if not cap.isOpened():
            print(f"[DETECTOR] Failed to open camera source: {source}")
            return

        print(f"[DETECTOR] Camera opened, starting detection loop")
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
                print(f"[DETECTOR] Inference error: {e}")
                continue

            # Update shared frame buffer (thread-safe)
            frame_manager.update(annotated_frame)

            # Periodic detection + snapshot callback (every 10s)
            if current_time - interval_start >= 10:
                try:
                    on_detection(head_count, fps)
                    on_snapshot(head_count, frame)
                except Exception as e:
                    print(f"[DETECTOR] Callback error: {e}")
                interval_start = current_time

        cap.release()
        print("[DETECTOR] Camera released")

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
