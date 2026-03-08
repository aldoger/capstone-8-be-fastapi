from fastapi import APIRouter
from app.schemas.detection_schema import AggregatedDetection
from app.services.aggregation_service import aggregator

router = APIRouter()


@router.post("/")
def receive_detection(data: AggregatedDetection):

    batch = aggregator.add_detection(data.detections)

    if batch:
        return {
            "message": "batch ready",
            "total_batch": len(batch),
            "detections": batch
        }

    return {
        "message": "stored",
        "buffer_size": aggregator.get_buffer_size()
    }


@router.get("/")
def get_detection_data():

    data = aggregator.get_detection_data()

    return {
        "total": len(data),
        "detections": data
    }