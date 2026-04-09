from app.core.stream_state import frame_state
import cv2

class CameraService:

    def __init__(self):
        pass

    def generate(self):
        while True:
            if frame_state is None:
                continue

            _, buffer = cv2.imencode(".jpg", frame_state)
            frame = buffer.tobytes()

            yield (b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

camera_service = CameraService()