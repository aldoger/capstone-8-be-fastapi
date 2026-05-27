import time
from app.core.detection_source import detection_source


class CameraService:

    def generate(self, source_id: str):
        """Generator that yields MJPEG frames for StreamingResponse.
        
        Streams frames from the DetectorRunner matching the given source_id.
        """
        runner = detection_source.get_runner(source_id)
        if runner is None:
            return

        while True:
            jpeg = runner.get_jpeg()

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