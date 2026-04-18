from fastapi import APIRouter
from app.schemas.source_schema import SourceData, ProbeResponse
from app.core.detection_source import detection_source

router = APIRouter()

@router.post("")
def receive_source(data: SourceData):
    source_id = data.id
    source_type = data.type
    source_url = data.url

    result = detection_source.add_detector_runner(source_id, source_type, source_url)
    return result
