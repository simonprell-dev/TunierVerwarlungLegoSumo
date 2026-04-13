from fastapi import FastAPI

from app.api.routes import router
from app.core.version import API_VERSION, SERVICE_VERSION

app = FastAPI(
    title="BauDoc PDF Analysis Service",
    version=SERVICE_VERSION,
    openapi_url=f"/{API_VERSION}/openapi.json",
    docs_url=f"/{API_VERSION}/docs",
)

app.include_router(router, prefix=f"/{API_VERSION}")


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "pdf-analysis-service", "status": "running", "api_version": API_VERSION}
