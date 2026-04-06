import requests
import cv2

def send_batch(url: str, payload: dict):
    response = requests.post(url, json=payload)
    return response.json()

def send_snapshot(url: str, filename: str, frame):
    _, buffer = cv2.imencode(".png", frame)

    files = {
        "snapshot_image": (filename, buffer.tobytes(), "image/png")
    }

    response = requests.post(url, files=files)
    print(response.status_code, response.text)