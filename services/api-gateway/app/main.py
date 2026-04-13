from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.version import router as version_router
from app.core.errors import install_error_handlers
from app.core.version import API_VERSION, SERVICE_NAME, SERVICE_VERSION

app = FastAPI(
    title="BauDoc API Gateway",
    version=SERVICE_VERSION,
    openapi_url=f"/{API_VERSION}/openapi.json",
    docs_url=f"/{API_VERSION}/docs",
)

install_error_handlers(app)


app.include_router(health_router, prefix=f"/{API_VERSION}")
app.include_router(version_router, prefix=f"/{API_VERSION}")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": SERVICE_NAME,
        "message": "BauDoc API Gateway is running",
        "api_version": API_VERSION,
    }
