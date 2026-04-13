from collections.abc import Callable
from uuid import UUID

from app.application.dtos import DocumentPersistenceDTO, DocumentSectionPersistenceDTO
from app.domain.ports.repositories import DocumentRepository

SqlExecutor = Callable[[str, dict], None]
SqlFetcher = Callable[[str, dict], dict | None]


class PostgresDocumentRepository(DocumentRepository):
    """Kapselt SQL für Dokumente/Sections vollständig in der Infrastruktur-Schicht."""

    def __init__(self, execute: SqlExecutor, fetch_one: SqlFetcher) -> None:
        self._execute = execute
        self._fetch_one = fetch_one

    def upsert_document(self, dto: DocumentPersistenceDTO) -> None:
        self._execute(
            """
            INSERT INTO documents (
                id, tenant_id, owner_user_id, title, source_filename, storage_path, mime_type,
                checksum_sha256, status, version, processing_state, extracted_pdf_data, metadata,
                created_at, updated_at
            ) VALUES (
                %(id)s, %(tenant_id)s, %(owner_user_id)s, %(title)s, %(source_filename)s,
                %(storage_path)s, %(mime_type)s, %(checksum_sha256)s, %(status)s, %(version)s,
                %(processing_state)s::jsonb, %(extracted_pdf_data)s::jsonb, %(metadata)s::jsonb,
                %(created_at)s, %(updated_at)s
            )
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                source_filename = EXCLUDED.source_filename,
                storage_path = EXCLUDED.storage_path,
                status = EXCLUDED.status,
                version = EXCLUDED.version,
                processing_state = EXCLUDED.processing_state,
                extracted_pdf_data = EXCLUDED.extracted_pdf_data,
                metadata = EXCLUDED.metadata,
                updated_at = EXCLUDED.updated_at
            """,
            dto.__dict__,
        )

    def replace_sections(
        self,
        document_id: UUID,
        sections: list[DocumentSectionPersistenceDTO],
    ) -> None:
        self._execute(
            "DELETE FROM document_sections WHERE document_id = %(document_id)s",
            {"document_id": document_id},
        )

        for section in sections:
            self._execute(
                """
                INSERT INTO document_sections (
                    id, document_id, section_key, heading, content, page_from,
                    page_to, metadata, position_index
                ) VALUES (
                    %(id)s, %(document_id)s, %(section_key)s, %(heading)s, %(content)s,
                    %(page_from)s, %(page_to)s, %(metadata)s::jsonb, %(position_index)s
                )
                """,
                section.__dict__,
            )

    def find_by_tenant_and_checksum(
        self,
        *,
        tenant_id: UUID,
        checksum_sha256: str,
    ) -> DocumentPersistenceDTO | None:
        row = self._fetch_one(
            """
            SELECT id, tenant_id, owner_user_id, title, source_filename, storage_path, mime_type,
                   checksum_sha256, status, version, processing_state, extracted_pdf_data,
                   metadata, created_at, updated_at
              FROM documents
             WHERE tenant_id = %(tenant_id)s
               AND checksum_sha256 = %(checksum_sha256)s
             ORDER BY created_at DESC
             LIMIT 1
            """,
            {"tenant_id": tenant_id, "checksum_sha256": checksum_sha256},
        )
        if not row:
            return None

        return DocumentPersistenceDTO(**row)
