import cv2
import supervision as sv
from rfdetr import RFDETRNano
from rfdetr.assets.coco_classes import COCO_CLASSES
import time
from datetime import datetime
from ultralytics import YOLO
import sys
import os
import requests, json
from dotenv import load_dotenv
import app.core.stream_state as state

load_dotenv()

pick_model = sys.argv[1]
base_url = os.getenv("BASE_URL")
source = "webcam"

def send_detection(payload_detection):
    requests.post(
        f"{base_url}/head-detection/{source}",
        json=payload_detection
    )

def send_snapshot(payload_snapshot, filename, frame):
    _, buffer = cv2.imencode(".png", frame)

    files = {
        "snapshot_image": (filename, buffer.tobytes(), "image/png")
    }

    data = {
        "snapshot": json.dumps(payload_snapshot)
    }

    requests.post(
        f"{base_url}/snapshot/{source}",
        files=files,
        data=data
    )

if pick_model == "yolo":
    model = YOLO("yolo.pt")
    model_type = "YOLO"

else:
    model = RFDETRNano(pretrain_weights="checkpoint_best_total.pth")

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

        state.frame_state = frame

    else:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        detections = model.predict(frame_rgb, threshold=0.5)

        head_counts = sum(1 for c in detections.class_id if c == 1)

        labels = [COCO_CLASSES[class_id] for class_id in detections.class_id]

        annotated_frame = box_annotator.annotate(frame_rgb, detections)
        annotated_frame = label_annotator.annotate(
            annotated_frame, detections, labels
        )

        state.frame_state = frame

    total_heads = head_counts

    if current_time - interval_start >= 10:
        
        snapshot_filename = f'snapshots/photo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        payload_detection = {
            "head_count": int(total_heads),
            "current_fps": float(fps),  
            "timestamp": datetime.now().isoformat()
        }

        payload_snapshot = {
            "head_count_at_time": int(total_heads),
            "image_path": snapshot_filename
        }

        try:
            send_detection(payload_detection)
            send_snapshot(payload_snapshot, snapshot_filename, frame)
        except Exception as e:
            print("Error sending data:", e)

        interval_start = current_time

    cv2.imshow(model_type, annotated_frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()