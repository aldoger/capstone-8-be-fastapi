from fastapi import FastAPI
from app.api.endpoints import detection

app = FastAPI()

app.include_router(detection.router, prefix="/detection", tags=["Detection"])