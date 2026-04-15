from fastapi import APIRouter, Path, HTTPException
from fastapi.responses import StreamingResponse
from app.services.camera_service import camera_service
from app.core.detection_source import detection_source

router = APIRouter()

@router.get("/stream/{id}")
def stream(id: str = Path(...)):
    if not detection_source.get_runner(id):
        raise HTTPException(
            status_code=404,
            detail="Camera source not found"
        )

    return StreamingResponse(
        camera_service.generate(id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )