from fastapi import APIRouter
from app.schemas.detection_schema import SnapshotWithDetection
from app.services.aggregation_service import aggregator

router = APIRouter()


@router.post("")
def receive_detection(data: SnapshotWithDetection):

    aggregator.add_detection(data=data)
