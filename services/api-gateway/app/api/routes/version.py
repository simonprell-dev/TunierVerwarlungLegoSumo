from fastapi import APIRouter

from app.api.schemas.common import VersionResponse
from app.application.commands.get_version_command import GetVersionCommand
from app.application.services.version_service import VersionService
from app.core.version import API_VERSION, SERVICE_NAME, SERVICE_VERSION

router = APIRouter(prefix="/version", tags=["version"])
version_service = VersionService()


@router.get("", response_model=VersionResponse)
def version() -> VersionResponse:
    data = version_service.execute(
        GetVersionCommand(service=SERVICE_NAME, version=SERVICE_VERSION, api_version=API_VERSION)
    )
    return VersionResponse(**data)
