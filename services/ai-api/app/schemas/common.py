from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class ServiceStatus(BaseModel):
    status: str  # "ok" | "degraded" | "down"
    latency_ms: Optional[float] = None


class HealthResponse(BaseModel):
    status: str
    services: dict[str, ServiceStatus]
