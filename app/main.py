from fastapi import FastAPI
from app.routers.detection import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.include_router(router=router, prefix="/detection", tags=["Detection"])