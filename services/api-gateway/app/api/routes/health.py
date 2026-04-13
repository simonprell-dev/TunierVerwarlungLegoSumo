from fastapi import APIRouter

from app.api.schemas.common import HealthResponse
from app.core.version import SERVICE_NAME
from app.domain.services.health_service import HealthService

router = APIRouter(prefix="/health", tags=["health"])
health_service = HealthService()


@router.get("", response_model=HealthResponse)
def health() -> HealthResponse:
    state = health_service.check(service_name=SERVICE_NAME)
    return HealthResponse(status=state.status, service=state.service_name)
