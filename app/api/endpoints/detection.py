from fastapi import APIRouter
from app.schemas.detection_schema import Detection
from app.services.aggregation_service import aggregator

router = APIRouter()


@router.post("/")
def receive_detection(data: Detection):

    aggregator.add_detection(data)

    return {
        "message": "Detection stored",
        "buffer_size": aggregator.get_buffer_size()
    }


@router.get("/")
def get_detection_data():

    data = aggregator.get_detection_data()

    return {
        "total": len(data),
        "detections": data
    }