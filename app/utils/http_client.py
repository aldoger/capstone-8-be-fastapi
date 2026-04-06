import requests
from fastapi import File, UploadFile

def send_batch(url: str, payload: dict):
    response = requests.post(url, json=payload)
    return response.json()

def send_snapshot(url: str, image: UploadFile = File(...)):
    file_content = await image.read()

    files = {"file": (file.filename, file_content, file.content_type)}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, files=files)

    return {"status": response.status_code, "response": response.json()}