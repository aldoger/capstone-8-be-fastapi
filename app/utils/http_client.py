import requests


def send_batch(url: str, payload: dict):
    response = requests.post(url, json=payload)
    return response.json()