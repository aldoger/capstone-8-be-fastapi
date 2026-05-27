import requests
import cv2
import json

def send_batch(url: str, payload):
    requests.post(url, json=payload)

def send_snapshot(url: str, snapshot_data, filename, frame):
    _, buffer = cv2.imencode(".png", frame)

    files = {
        "snapshot_image": (filename, buffer.tobytes(), "image/png")
    }

    data = {
        "snapshot_data": json.dumps(snapshot_data)
    }

    requests.post(url, files=files, data=data)