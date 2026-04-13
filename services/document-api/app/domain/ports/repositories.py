from typing import Protocol
from uuid import UUID

from app.application.dtos import (
    DocumentPersistenceDTO,
    DocumentSectionPersistenceDTO,
    JobPersistenceDTO,
)


class DocumentRepository(Protocol):
    def upsert_document(self, dto: DocumentPersistenceDTO) -> None:
        ...

    def replace_sections(
        self,
        document_id: UUID,
        sections: list[DocumentSectionPersistenceDTO],
    ) -> None:
        ...

    def find_by_tenant_and_checksum(
        self,
        *,
        tenant_id: UUID,
        checksum_sha256: str,
    ) -> DocumentPersistenceDTO | None:
        ...


class JobRepository(Protocol):
    def upsert_job(self, dto: JobPersistenceDTO) -> None:
        ...
