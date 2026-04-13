from app.domain.ports.queue import IngestionQueuePort


class InMemoryIngestionQueueAdapter(IngestionQueuePort):
    def __init__(self) -> None:
        self.messages: list[dict[str, str]] = []

    def enqueue_document_ingestion(self, *, tenant_id: str, document_id: str, checksum_sha256: str) -> None:
        self.messages.append(
            {
                "tenant_id": tenant_id,
                "document_id": document_id,
                "checksum_sha256": checksum_sha256,
            },
        )
