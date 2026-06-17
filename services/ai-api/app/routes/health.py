import time
import asyncio
from fastapi import APIRouter
from app.schemas.common import HealthResponse, ServiceStatus
from app.services import ollama_service, huggingface_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    results = await asyncio.gather(
        _check_ollama(),
        _check_huggingface(),
        return_exceptions=True,
    )

    services = {
        "ollama": results[0] if isinstance(results[0], ServiceStatus) else ServiceStatus(status="down"),
        "huggingface": results[1] if isinstance(results[1], ServiceStatus) else ServiceStatus(status="down"),
    }

    global_status = "ok" if all(s.status == "ok" for s in services.values()) else "degraded"
    if all(s.status == "down" for s in services.values()):
        global_status = "down"

    return HealthResponse(status=global_status, services=services)


async def _check_ollama() -> ServiceStatus:
    try:
        latency = await ollama_service.ping()
        return ServiceStatus(status="ok", latency_ms=latency)
    except Exception:
        return ServiceStatus(status="down")


async def _check_huggingface() -> ServiceStatus:
    try:
        latency = await huggingface_service.ping()
        return ServiceStatus(status="ok", latency_ms=latency)
    except Exception:
        return ServiceStatus(status="down")
