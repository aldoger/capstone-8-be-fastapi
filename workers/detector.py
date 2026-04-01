import cv2
import time
import requests
from datetime import datetime
from ultralytics import YOLO

API_URL = "http://localhost:8000/detection"

model = YOLO("yolo.pt")
cap = cv2.VideoCapture(0)

last_time = 0
interval_start = time.time()

model_name = "YOLO"
source = "web cam"  # nanti ganti

total_heads = 0
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    current_time = time.time()
    fps = 1 / (current_time - last_time) if last_time > 0 else 0
    last_time = current_time

    result = model(frame)
    annotated_frame = result[0].plot()
    boxes = result[0].boxes

    head_counts = 0
    if boxes is not None and boxes.cls is not None:
        head_counts = int((boxes.cls == 1).sum())

    total_heads = head_counts
    frame_count += 1

    if current_time - interval_start >= 10:

        payload = {
            "source": "webcam",
            "model_type": "YOLO",
            "result": {
                "head_count": int(total_heads),  
                "fps": f"{fps:.2f}",
                "timestamp": datetime.now().isoformat()
            }
        }

        try:
            response = requests.post(API_URL, json=payload)
            print("Sent:", payload, "Response:", response.status_code)
        except Exception as e:
            print("Error sending data:", e)

        interval_start = current_time
        accumulated_heads = 0
        frame_count = 0

    print(f"Heads: {total_heads}, FPS: {fps:.2f}")

    cv2.imshow(model_name, annotated_frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()