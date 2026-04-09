import threading
import cv2
import numpy as np


class FrameManager:
    """Thread-safe frame buffer for sharing frames between detector thread and MJPEG stream."""

    def __init__(self):
        self._lock = threading.Lock()
        self._frame: np.ndarray | None = None
        self._jpeg: bytes | None = None

    def update(self, frame: np.ndarray):
        """Called by detector thread to update the latest annotated frame."""
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        with self._lock:
            self._frame = frame
            self._jpeg = buffer.tobytes()

    def get_jpeg(self) -> bytes | None:
        """Called by MJPEG streaming endpoint. Returns JPEG bytes or None."""
        with self._lock:
            return self._jpeg

    def get_frame(self) -> np.ndarray | None:
        """Get raw numpy frame (for snapshot)."""
        with self._lock:
            return self._frame.copy() if self._frame is not None else None


frame_manager = FrameManager()
