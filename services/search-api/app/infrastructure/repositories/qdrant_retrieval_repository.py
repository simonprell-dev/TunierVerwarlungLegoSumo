from dataclasses import dataclass
from math import sqrt
from typing import Any

from app.domain.models.retrieval import (
    ChunkDocument,
    HybridSearchQuery,
    RetrievalHit,
)
from app.domain.ports.retrieval_repository import RetrievalRepository


@dataclass(frozen=True)
class QdrantPoint:
    point_id: str
    vector: list[float]
    payload: dict[str, Any]


class InMemoryQdrantRetrievalRepository(RetrievalRepository):
    """Qdrant-kompatible Retrieval-Grenze fuer Hybrid Search.

    Diese In-Memory-Implementierung bildet das Vektor- und Payload-Schema ab,
    sodass spaetere echte Qdrant-Clients dieselbe fachliche Schnittstelle nutzen.
    """

    def __init__(self) -> None:
        self._points: dict[str, QdrantPoint] = {}

    def upsert_chunks(self, chunks: list[ChunkDocument]) -> None:
        for chunk in chunks:
            payload = {
                "tenant_id": chunk.tenant_id,
                "document_id": chunk.document_id,
                "section_id": chunk.section_id,
                "source_uri": chunk.source_uri,
                "content": chunk.content,
                "metadata": chunk.metadata,
                "embedding_model": chunk.embedding.model_name,
                "embedding_version": chunk.embedding.model_version,
            }
            self._points[chunk.chunk_id] = QdrantPoint(
                point_id=chunk.chunk_id,
                vector=chunk.embedding.vector,
                payload=payload,
            )

    def hybrid_search(self, query: HybridSearchQuery) -> list[RetrievalHit]:
        scored_hits: list[RetrievalHit] = []
        normalized_text = query.query_text.lower().strip()

        for point in self._points.values():
            if point.payload["tenant_id"] != query.tenant_id:
                continue

            if not self._passes_metadata_filters(
                metadata=point.payload["metadata"],
                filters=query.metadata_filters,
            ):
                continue

            semantic_score = self._cosine_similarity(query.query_vector, point.vector)
            keyword_score = self._keyword_overlap(
                query_text=normalized_text,
                content=point.payload["content"],
            )
            hybrid_score = (semantic_score * 0.7) + (keyword_score * 0.3)

            scored_hits.append(
                RetrievalHit(
                    chunk_id=point.point_id,
                    document_id=point.payload["document_id"],
                    section_id=point.payload["section_id"],
                    source_uri=point.payload["source_uri"],
                    score=hybrid_score,
                    content=point.payload["content"],
                    metadata=point.payload["metadata"],
                ),
            )

        scored_hits.sort(key=lambda hit: hit.score, reverse=True)
        return scored_hits[: query.limit]

    def list_chunk_ids_by_embedding_version(
        self,
        *,
        tenant_id: str,
        embedding_version: str,
    ) -> list[str]:
        chunk_ids: list[str] = []
        for point in self._points.values():
            if point.payload["tenant_id"] != tenant_id:
                continue
            if point.payload["embedding_version"] != embedding_version:
                continue
            chunk_ids.append(point.point_id)
        return chunk_ids

    def _passes_metadata_filters(
        self,
        *,
        metadata: dict[str, Any],
        filters: dict[str, Any] | None,
    ) -> bool:
        if not filters:
            return True

        for key, value in filters.items():
            if metadata.get(key) != value:
                return False
        return True

    def _cosine_similarity(self, query_vector: list[float], stored_vector: list[float]) -> float:
        if len(query_vector) != len(stored_vector):
            return 0.0

        dot_product = sum(a * b for a, b in zip(query_vector, stored_vector, strict=True))
        query_norm = sqrt(sum(value * value for value in query_vector))
        stored_norm = sqrt(sum(value * value for value in stored_vector))

        if query_norm == 0 or stored_norm == 0:
            return 0.0

        return dot_product / (query_norm * stored_norm)

    def _keyword_overlap(self, *, query_text: str, content: str) -> float:
        query_tokens = {token for token in query_text.split() if token}
        content_tokens = {token for token in content.lower().split() if token}

        if not query_tokens:
            return 0.0

        return len(query_tokens.intersection(content_tokens)) / len(query_tokens)
