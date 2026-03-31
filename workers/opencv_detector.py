import cv2
import time
import requests
from datetime import datetime
from ultralytics import YOLO

API_URL = "http://localhost:8000/detection"

model = YOLO("yolo.pt")
cap = cv2.VideoCapture(0)
source = "web cam"

last_time = 0

model_name = "YOLO"

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

    total_heads = 0

    if boxes is not None and boxes.cls is not None:
        total_heads = int((boxes.cls == 1).sum())

    print(f"Total heads: {total_heads}, FPS: {fps:.2f}")

    cv2.imshow(model_name, annotated_frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()