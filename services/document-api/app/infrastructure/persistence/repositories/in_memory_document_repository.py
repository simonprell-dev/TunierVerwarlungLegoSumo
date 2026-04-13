from app.application.dtos import DocumentPersistenceDTO, DocumentSectionPersistenceDTO
from app.domain.ports.repositories import DocumentRepository


class InMemoryDocumentRepository(DocumentRepository):
    def __init__(self) -> None:
        self.documents: dict[str, DocumentPersistenceDTO] = {}
        self.sections: dict[str, list[DocumentSectionPersistenceDTO]] = {}

    def upsert_document(self, dto: DocumentPersistenceDTO) -> None:
        self.documents[str(dto.id)] = dto

    def replace_sections(
        self,
        document_id,
        sections: list[DocumentSectionPersistenceDTO],
    ) -> None:
        self.sections[str(document_id)] = sections

    def find_by_tenant_and_checksum(self, *, tenant_id, checksum_sha256: str) -> DocumentPersistenceDTO | None:
        for document in self.documents.values():
            if document.tenant_id == tenant_id and document.checksum_sha256 == checksum_sha256:
                return document
        return None
