import cv2
import supervision as sv
from rfdetr import RFDETRNano
import torch
import time
import requests
from datetime import datetime
from ultralytics import YOLO
import sys
import os

os.makedirs("pictures", exist_ok=True)

pick_model = sys.argv[1]
API_URL = "http://localhost:8000/detection"

if pick_model == "yolo":
    model = YOLO("yolo.pt")
    model_type = "YOLO"

else:
    model = RFDETRNano(pretrained=False)

    checkpoint = torch.load("checkpoint_best_total.pth", map_location="cpu")

    state_dict = checkpoint.get("model", checkpoint)

    new_state_dict = {}
    for k, v in state_dict.items():
        new_state_dict[k.replace("module.", "")] = v

    model.model.load_state_dict(new_state_dict)
    model.model.eval()

    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()

    model_type = "RF-DETR"


cap = cv2.VideoCapture(0)

last_time = 0
interval_start = time.time()

total_heads = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    current_time = time.time()
    fps = 1 / (current_time - last_time) if last_time > 0 else 0
    last_time = current_time


    if pick_model == "yolo":
        result = model.track(frame, persist=True)
        annotated_frame = result[0].plot()
        boxes = result[0].boxes

        head_counts = 0
        if boxes is not None and boxes.cls is not None:
            head_counts = int((boxes.cls == 1).sum())

    else:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        detections = model.predict(frame_rgb, threshold=0.5)

        head_counts = sum(1 for c in detections.class_id if c == 1)

        labels = [str(c) for c in detections.class_id]

        annotated_frame = box_annotator.annotate(frame.copy(), detections)
        annotated_frame = label_annotator.annotate(
            annotated_frame, detections, labels
        )

    total_heads = head_counts

    if current_time - interval_start >= 10:
        
        cv2.imwrite(f'pictures/photo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png', frame)

        payload = {
            "source": "webcam",
            "model_type": model_type,
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

    cv2.imshow(model_type, annotated_frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()