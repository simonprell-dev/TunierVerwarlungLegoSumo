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


class JobRepository(Protocol):
    def upsert_job(self, dto: JobPersistenceDTO) -> None:
        ...
