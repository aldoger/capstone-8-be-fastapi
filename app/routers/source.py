from fastapi import APIRouter
from app.schemas.source_schema import SourceData, ProbeResponse
from app.core.detection_source import detection_source

router = APIRouter()

@router.post("")
def receive_source(data: SourceData):
    result = detection_source.add_detector_runner(
        id=data.id,
        type_source=data.type,
        url=data.url
    )
    if result is False:
        return ProbeResponse(
            exists=True,
            detail="source already exist"
        )
    return ProbeResponse(
        exists=False,
        detail="source added and detection thread started"
    )
