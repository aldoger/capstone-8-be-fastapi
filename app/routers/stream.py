from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.camera_service import camera_service

router = APIRouter()

@router.get("/stream")
def stream():
    return StreamingResponse(
        camera_service.generate(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
    