from fastapi import APIRouter

router = APIRouter()

@router.post("/sources")
def receive_source(data):
    pass