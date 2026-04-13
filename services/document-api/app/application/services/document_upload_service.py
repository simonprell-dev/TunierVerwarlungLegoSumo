from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid4

from app.application.dtos import DocumentPersistenceDTO, JobPersistenceDTO
from app.domain.ports.queue import IngestionQueuePort
from app.domain.ports.repositories import DocumentRepository, JobRepository
from app.domain.ports.storage import FileStoragePort

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "text/plain",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_UPLOAD_SIZE_BYTES = 20 * 1024 * 1024


@dataclass(frozen=True)
class UploadResult:
    document_id: UUID
    job_id: UUID | None
    filename: str
    checksum_sha256: str
    storage_path: str
    status: str


class UploadValidationError(ValueError):
    pass


class DocumentUploadService:
    def __init__(
        self,
        *,
        document_repository: DocumentRepository,
        job_repository: JobRepository,
        file_storage: FileStoragePort,
        ingestion_queue: IngestionQueuePort,
    ) -> None:
        self._document_repository = document_repository
        self._job_repository = job_repository
        self._file_storage = file_storage
        self._ingestion_queue = ingestion_queue

    def register_upload(
        self,
        *,
        tenant_id: UUID,
        owner_user_id: UUID,
        filename: str,
        mime_type: str,
        content: bytes,
        title: str | None,
    ) -> UploadResult:
        self._validate_upload(filename=filename, mime_type=mime_type, content=content)

        checksum_sha256 = sha256(content).hexdigest()
        existing = self._document_repository.find_by_tenant_and_checksum(
            tenant_id=tenant_id,
            checksum_sha256=checksum_sha256,
        )

        if existing:
            return UploadResult(
                document_id=existing.id,
                job_id=None,
                filename=existing.source_filename,
                checksum_sha256=existing.checksum_sha256,
                storage_path=existing.storage_path,
                status="duplicate",
            )

        now = datetime.now(tz=UTC)
        document_id = uuid4()

        stored_file = self._file_storage.save(
            tenant_id=str(tenant_id),
            document_id=str(document_id),
            filename=filename,
            content=content,
        )

        document_dto = DocumentPersistenceDTO(
            id=document_id,
            tenant_id=tenant_id,
            owner_user_id=owner_user_id,
            title=title or Path(filename).stem,
            source_filename=filename,
            storage_path=stored_file.storage_path,
            mime_type=mime_type,
            checksum_sha256=checksum_sha256,
            status="uploaded",
            version=1,
            processing_state={"stage": "uploaded"},
            extracted_pdf_data={},
            metadata={"size_bytes": stored_file.size_bytes},
            created_at=now,
            updated_at=now,
        )
        self._document_repository.upsert_document(document_dto)

        job_id = uuid4()
        job_dto = JobPersistenceDTO(
            id=job_id,
            tenant_id=tenant_id,
            document_id=document_id,
            job_type="document_ingestion",
            status="queued",
            requested_by_user_id=owner_user_id,
            payload={"document_id": str(document_id), "storage_path": stored_file.storage_path},
            result_payload={},
            error_payload={},
            attempts=0,
            max_attempts=3,
            scheduled_at=now,
            started_at=None,
            finished_at=None,
            created_at=now,
            updated_at=now,
        )
        self._job_repository.upsert_job(job_dto)
        self._ingestion_queue.enqueue_document_ingestion(
            tenant_id=str(tenant_id),
            document_id=str(document_id),
            checksum_sha256=checksum_sha256,
        )

        return UploadResult(
            document_id=document_id,
            job_id=job_id,
            filename=filename,
            checksum_sha256=checksum_sha256,
            storage_path=stored_file.storage_path,
            status="registered",
        )

    def _validate_upload(self, *, filename: str, mime_type: str, content: bytes) -> None:
        if not filename:
            raise UploadValidationError("filename must not be empty")

        if mime_type not in ALLOWED_MIME_TYPES:
            raise UploadValidationError(f"mime type '{mime_type}' is not allowed")

        if len(content) == 0:
            raise UploadValidationError("file must not be empty")

        if len(content) > MAX_UPLOAD_SIZE_BYTES:
            raise UploadValidationError(
                f"file exceeds maximum size of {MAX_UPLOAD_SIZE_BYTES} bytes",
            )
