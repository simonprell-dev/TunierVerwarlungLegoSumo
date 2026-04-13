from typing import Protocol

from app.domain.models.retrieval import (
    ChunkDocument,
    HybridSearchQuery,
    RetrievalHit,
)


class RetrievalRepository(Protocol):
    def upsert_chunks(self, chunks: list[ChunkDocument]) -> None:
        ...

    def hybrid_search(self, query: HybridSearchQuery) -> list[RetrievalHit]:
        ...

    def list_chunk_ids_by_embedding_version(
        self,
        *,
        tenant_id: str,
        embedding_version: str,
    ) -> list[str]:
        ...
