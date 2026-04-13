from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class DocumentPersistenceDTO:
    id: UUID
    tenant_id: UUID
    owner_user_id: UUID
    title: str
    source_filename: str
    storage_path: str
    mime_type: str
    checksum_sha256: str
    status: str
    version: int
    processing_state: dict
    extracted_pdf_data: dict
    metadata: dict
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class DocumentSectionPersistenceDTO:
    id: UUID
    document_id: UUID
    section_key: str
    heading: str | None
    content: str | None
    page_from: int | None
    page_to: int | None
    metadata: dict
    position_index: int


@dataclass(frozen=True)
class JobPersistenceDTO:
    id: UUID
    tenant_id: UUID
    document_id: UUID | None
    job_type: str
    status: str
    requested_by_user_id: UUID | None
    payload: dict
    result_payload: dict
    error_payload: dict
    attempts: int
    max_attempts: int
    scheduled_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime
