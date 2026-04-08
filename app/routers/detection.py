from fastapi import APIRouter, UploadFile, File, Form, Path
import json
from app.schemas.detection_schema import DetectionResult, SnapshotData
from app.services.detection_service import detection_service

router = APIRouter()


@router.post("/head-detection/{source}")
def receive_head_detection(
    source: str = Path(...),
    data: DetectionResult = ...
):
    detection_service.send_head_detection(data=data, type_source=source)
    return {"status": "ok"}


@router.post("/snapshot/{source}")
async def receive_snapshot_detection(
    source: str = Path(...),
    snapshot_image: UploadFile = File(...),
    snapshot: str = Form(...)
):
    try:
        snapshot_data = SnapshotData(**json.loads(snapshot))
        image_bytes = await snapshot_image.read()

        detection_service.send_snapshot_data(
            snapshot_data,
            source,
            snapshot_image.filename,
            image_bytes
        )

        return {"status": "ok"}

    except Exception as e:
        return {"error": str(e)}