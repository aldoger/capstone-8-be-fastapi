from fastapi import APIRouter
from app.schemas.detection_schema import DetectionResult
from app.services.aggregation_service import aggregator

router = APIRouter()


@router.post("")
def receive_detection(data: DetectionResult):

    aggregator.add_detection(data)

    return {
        "message": "stored",
    }


@router.get("")
def get_detection_data():

    data = aggregator.get_detection_data()

    if data is None:
        return {
            "detection": None
        }

    return {
        "detection": data
    }