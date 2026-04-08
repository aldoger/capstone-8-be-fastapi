from dotenv import load_dotenv
import os

load_dotenv()

from fastapi import FastAPI
from app.routers.detection import router
from app.schemas.source_schema import SourceData
from app.services.detection_service import detection_service
import httpx


core_url = os.getenv("BE_CORE_URL")

app = FastAPI()


@app.on_event("startup")
async def get_source():
    async with httpx.AsyncClient() as client:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{core_url}/sources", timeout=5.0)
                response.raise_for_status()

                data = response.json()

                sources = [
                    SourceData(
                        id=src["id"],
                        type=src["type"]
                    )
                    for src in data["sources"]
                ]

                detection_service.build_source_map(sources)

                print("[STARTUP] Sources loaded")

        except Exception as e:
            print("[FATAL] Failed to fetch sources:", e)
            raise RuntimeError("Startup failed: cannot load sources")

app.include_router(router=router, prefix="/detection", tags=["Detection"])