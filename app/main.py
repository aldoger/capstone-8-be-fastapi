from dotenv import load_dotenv
import os

load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
import app.routers.detection as detection_router
import app.routers.stream as stream_router
import app.routers.source as source_router
from app.schemas.source_schema import SourceData
from app.services.detection_service import detection_service
from app.core.frame_manager import frame_manager
from app.core.detector_runner import DetectorRunner
import httpx


core_url = os.getenv("BE_CORE_URL")
model_name = os.getenv("MODEL_NAME", "yolo")

detector = DetectorRunner(model_name=model_name)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    async with httpx.AsyncClient() as client:
        try:
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

    # Start detector thread
    detector.start(
        frame_manager=frame_manager,
        on_detection_callback=detection_service.handle_detection,
        on_snapshot_callback=detection_service.handle_snapshot,
    )
    print("[STARTUP] Detector thread started")

    yield

    # --- Shutdown ---
    detector.stop()
    print("[SHUTDOWN] Detector thread stopped")


app = FastAPI(lifespan=lifespan)

app.include_router(router=detection_router.router, prefix="/detection", tags=["Detection"])
app.include_router(router=source_router.router, prefix="/probe", tags=["Sources"])
app.include_router(router=stream_router.router, prefix="/camera", tags=["Stream"])