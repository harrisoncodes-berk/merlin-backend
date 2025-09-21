from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from app.settings import get_settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    time: str
    env: str


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    s = get_settings()
    return HealthResponse(
        status="ok",
        service=s.project_name,
        version=s.version,
        time=datetime.now(timezone.utc).isoformat(),
        env=s.env,
    )
