import os
from dotenv import load_dotenv

load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
import app.routers.health as health_router
import app.routers.stream as stream_router
import app.routers.source as source_router
from app.schemas.source_schema import SourceData
from app.core.detection_source import detection_source
import httpx


core_url = os.getenv("BE_CORE_URL")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{core_url}/sources",
                timeout=5.0
            )

            response.raise_for_status()

            data = response.json()

            if not data or not data.get("sources"):
                print("[STARTUP] No sources found, skipping detector startup")

            else:
                sources = [
                    SourceData(
                        id=src["id"],
                        name=src["name"],
                        type=src["type"],
                        url=src.get("url"),
                    )
                    for src in data["sources"]
                ]

                # Start detector threads
                for source in sources:
                    detection_source.add_detector_runner(
                        id=source.id,
                        type_source=source.type,
                        url=source.url,
                    )

                print(
                    f"[STARTUP] {len(sources)} sources loaded, "
                    "detection threads started"
                )

        except httpx.TimeoutException:
            print("[WARNING] Source server timeout, skipping source loading")

        except httpx.ConnectError:
            print("[WARNING] Cannot connect to source server, skipping source loading")

        except Exception as e:
            print(f"[WARNING] Failed to load sources: {e}")

    # Server still starts normally
    yield

    # --- Shutdown ---
    detection_source.stop_all()
    print("[SHUTDOWN] All detection threads stopped")


app = FastAPI(lifespan=lifespan)

app.include_router(router=health_router.router, prefix="/health-check", tags=["Health"])
app.include_router(router=source_router.router, prefix="/probe", tags=["Sources"])
app.include_router(router=stream_router.router, prefix="/camera", tags=["Stream"])