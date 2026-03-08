import cv2
import time
import uuid
import requests
from datetime import datetime

API_URL = "http://localhost:8000/detection"

cap = cv2.VideoCapture(0)

last_time = 0

while True:
    ret, frame = cap.read()

    if not ret:
        break

    now = time.time()

    if now - last_time > 5:

        payload = {
            "detections": [
                {
                    "id": str(uuid.uuid4()),
                    "object": "person",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        }

        try:
            requests.post(API_URL, json=payload)
        except Exception as e:
            print("Error:", e)

        last_time = now

    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()