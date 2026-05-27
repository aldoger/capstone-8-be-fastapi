from fastapi import APIRouter
from app.schemas.source_schema import SourceData
from app.core.detection_source import detection_source

router = APIRouter()

@router.post("")
def receive_source(data: SourceData):
    source_id = data.id
    source_type = data.type
    source_url = data.url

    result = detection_source.add_detector_runner(source_id, source_type, source_url)
    return result

@router.post("/video")
def receive_source_from_video(data: SourceData):
    pass

@router.post("/remove/{id}")
def remove_source(id: str):
    result = detection_source.remove_runner(id=id)
    if not result:
        return {"message": "error cannot remove source"}
    return {"message": "source removed"}
    
