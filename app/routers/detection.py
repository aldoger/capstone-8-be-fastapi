from fastapi import APIRouter
from app.schemas.detection_schema import DetectionResult, SnapshotData
from app.services.aggregation_service import aggregator

router = APIRouter()


@router.post("")
def receive_detection(detection: DetectionResult, snapshot: SnapshotData, filename, frame):

    aggregator.add_detection(detection, snapshot, filename, frame)
