import time
from app.core.frame_manager import frame_manager


class CameraService:

    def generate(self):
        """Generator that yields MJPEG frames for StreamingResponse."""
        while True:
            jpeg = frame_manager.get_jpeg()

            if jpeg is None:
                time.sleep(0.03)
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                jpeg +
                b"\r\n"
            )


camera_service = CameraService()