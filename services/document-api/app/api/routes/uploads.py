from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.api.schemas.upload import UploadResponse
from app.application.services.document_upload_service import (
    DocumentUploadService,
    UploadValidationError,
)

router = APIRouter(prefix="/uploads", tags=["uploads"])


def build_upload_router(service: DocumentUploadService) -> APIRouter:
    @router.post("/documents", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
    async def upload_document(
        tenant_id: UUID = Form(...),
        owner_user_id: UUID = Form(...),
        title: str | None = Form(default=None),
        document: UploadFile = File(...),
    ) -> UploadResponse:
        try:
            content = await document.read()
            result = service.register_upload(
                tenant_id=tenant_id,
                owner_user_id=owner_user_id,
                filename=document.filename or "",
                mime_type=document.content_type or "",
                content=content,
                title=title,
            )
        except UploadValidationError as error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

        return UploadResponse(
            document_id=str(result.document_id),
            job_id=str(result.job_id) if result.job_id else None,
            filename=result.filename,
            checksum_sha256=result.checksum_sha256,
            storage_path=result.storage_path,
            status=result.status,
        )

    return router
