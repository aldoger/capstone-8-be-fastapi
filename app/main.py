from fastapi import FastAPI
from app.routers.detection import detection

app = FastAPI()

app.include_router(detection.router, prefix="/detection", tags=["Detection"])