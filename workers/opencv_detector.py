import cv2
import time
import uuid
import requests
from datetime import datetime
from ultralytics import YOLO

API_URL = "http://localhost:8000/detection"

model = YOLO("yolo.pt")
cap = cv2.VideoCapture(0)

last_time = 0


while True:
    ret, frame = cap.read()

    if not ret:
        break

    result = model(frame)

    annotated_frame = result[0].plot()
        
    cv2.imshow("YOLO", annotated_frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()