from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from app.routers.detection import router


app = FastAPI()

app.include_router(router=router, prefix="/detection", tags=["Detection"])