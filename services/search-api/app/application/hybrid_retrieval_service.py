from app.domain.models.retrieval import (
    ChunkDocument,
    HybridSearchQuery,
    ReindexPlan,
    RetrievalHit,
)
from app.domain.ports.retrieval_repository import RetrievalRepository


class HybridRetrievalService:
    def __init__(self, *, retrieval_repository: RetrievalRepository) -> None:
        self._retrieval_repository = retrieval_repository

    def index_chunks(self, chunks: list[ChunkDocument]) -> None:
        if not chunks:
            return

        self._retrieval_repository.upsert_chunks(chunks)

    def search(self, query: HybridSearchQuery) -> list[RetrievalHit]:
        if query.limit <= 0:
            return []

        return self._retrieval_repository.hybrid_search(query)

    def create_reindex_plan(
        self,
        *,
        tenant_id: str,
        from_embedding_version: str,
        to_embedding_version: str,
    ) -> ReindexPlan:
        affected_chunk_ids = self._retrieval_repository.list_chunk_ids_by_embedding_version(
            tenant_id=tenant_id,
            embedding_version=from_embedding_version,
        )
        return ReindexPlan(
            tenant_id=tenant_id,
            from_embedding_version=from_embedding_version,
            to_embedding_version=to_embedding_version,
            affected_chunk_ids=affected_chunk_ids,
        )
