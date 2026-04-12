from fastapi import APIRouter
from app.schemas.source_schema import SourceData
from app.services.detection_service import detection_service

router = APIRouter()

@router.post("")
def receive_source(data: SourceData):
    result = detection_service.add_source(data)
    if result is False:
        return {
            "exists": True,
            "detail": "source already exist"
        }
    return {
        "exists": False,
        "detail": "source added"
    }
