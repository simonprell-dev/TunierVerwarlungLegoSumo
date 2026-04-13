from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ChunkEmbedding:
    model_name: str
    model_version: str
    vector: list[float]


@dataclass(frozen=True)
class ChunkDocument:
    chunk_id: str
    tenant_id: str
    document_id: str
    section_id: str
    source_uri: str
    content: str
    metadata: dict[str, Any]
    embedding: ChunkEmbedding


@dataclass(frozen=True)
class HybridSearchQuery:
    tenant_id: str
    query_text: str
    query_vector: list[float]
    limit: int = 10
    metadata_filters: dict[str, Any] | None = None


@dataclass(frozen=True)
class RetrievalHit:
    chunk_id: str
    document_id: str
    section_id: str
    source_uri: str
    score: float
    content: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ReindexPlan:
    tenant_id: str
    from_embedding_version: str
    to_embedding_version: str
    affected_chunk_ids: list[str]
