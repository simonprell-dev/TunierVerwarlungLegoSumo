from fastapi import FastAPI

from app.api.routes.uploads import build_upload_router
from app.application.services.document_upload_service import DocumentUploadService
from app.core.version import API_VERSION, SERVICE_VERSION
from app.infrastructure.persistence.repositories.in_memory_document_repository import (
    InMemoryDocumentRepository,
)
from app.infrastructure.persistence.repositories.in_memory_job_repository import (
    InMemoryJobRepository,
)
from app.infrastructure.queue.in_memory_ingestion_queue import InMemoryIngestionQueueAdapter
from app.infrastructure.storage.local_file_storage import LocalFileStorageAdapter

app = FastAPI(
    title="BauDoc Document API",
    version=SERVICE_VERSION,
    openapi_url=f"/{API_VERSION}/openapi.json",
    docs_url=f"/{API_VERSION}/docs",
)


document_repository = InMemoryDocumentRepository()
job_repository = InMemoryJobRepository()
file_storage = LocalFileStorageAdapter(base_dir="/tmp/baudoc-document-api")
ingestion_queue = InMemoryIngestionQueueAdapter()

upload_service = DocumentUploadService(
    document_repository=document_repository,
    job_repository=job_repository,
    file_storage=file_storage,
    ingestion_queue=ingestion_queue,
)

app.include_router(build_upload_router(upload_service), prefix=f"/{API_VERSION}")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "document-api",
        "message": "BauDoc Document API is running",
        "api_version": API_VERSION,
    }
