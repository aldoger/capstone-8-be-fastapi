import threading
from uuid import UUID
import os

from app.core.detector_runner import DetectorRunner
from app.services.sender_service import sender_service
from app.services.go2rtc_service import go2rtc_service
from app.schemas.source_schema import ProbeResponse


class DetectionSource:
    """Central manager for all DetectorRunner instances.
    
    Each camera source gets its own runner (and thread). This class provides
    thread-safe add/get/remove/stop operations.
    """

    def __init__(self):
        self._runners: dict[str, DetectorRunner] = {}
        self._lock = threading.Lock()
        self._base_url = os.getenv("BASE_URL") 

    def add_detector_runner(self, id: UUID, type_source: str, url: str | None) -> ProbeResponse:
        """Create and start a new DetectorRunner for a given source.
        
        Returns False if a runner with the same ID already exists.
        """
        key = str(id)
        exists: bool
        exists=False

        # Every link is handed to go2rtc first; the runner then reads the
        # RTSP URL go2rtc serves back instead of the raw source link.
        if url is not None:
            url = go2rtc_service.add_stream(stream_id=key, source_url=url)
            type_source = "RTSP"

        with self._lock:
            if key in self._runners:
                exists = True
            runner = DetectorRunner(id=id, type_source=type_source, url=url)
            runner.start(
                on_detection_callback=sender_service.handle_detection,
                on_snapshot_callback=sender_service.handle_snapshot,
            )
            self._runners[key] = runner
        print(f"[DETECTION_SOURCE] Runner added for source {id}")
        camera_url = f"http://{self._base_url}/camera/stream/{id}"
        return ProbeResponse(
            exists=exists,
            detail="Source added",
            resolution="720p",
            url=camera_url,
            fps=13
        )
            
    def get_runner(self, id: str) -> DetectorRunner | None:
        """Get a runner by source ID. Returns None if not found."""
        return self._runners.get(str(id))

    def get_jpeg_by_id(self, id: str) -> bytes | None:
        """Shortcut to get JPEG frame from a specific runner."""
        runner = self.get_runner(id)
        if runner is None:
            return None
        return runner.get_jpeg()

    def remove_runner(self, id: str) -> bool:
        """Stop and remove a runner by source ID."""
        key = str(id)
        with self._lock:
            runner = self._runners.pop(key, None)
        if runner is None:
            return False
        runner.stop()
        print(f"[DETECTION_SOURCE] Runner removed for source {id}")
        return True

    def stop_all(self):
        """Stop all running DetectorRunner threads."""
        with self._lock:
            runners = list(self._runners.values())
        for runner in runners:
            runner.stop()
        print(f"[DETECTION_SOURCE] All runners stopped ({len(runners)} total)")


detection_source = DetectionSource()
