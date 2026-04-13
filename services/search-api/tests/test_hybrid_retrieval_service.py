from app.application.hybrid_retrieval_service import HybridRetrievalService
from app.domain.models.retrieval import ChunkDocument, ChunkEmbedding, HybridSearchQuery
from app.infrastructure.repositories.qdrant_retrieval_repository import (
    InMemoryQdrantRetrievalRepository,
)


def _chunk(
    *,
    chunk_id: str,
    content: str,
    vector: list[float],
    metadata: dict,
    tenant_id: str = "tenant-1",
    version: str = "e5-v1",
) -> ChunkDocument:
    return ChunkDocument(
        chunk_id=chunk_id,
        tenant_id=tenant_id,
        document_id="doc-1",
        section_id=f"section-{chunk_id}",
        source_uri=f"s3://docs/{chunk_id}.pdf#section",
        content=content,
        metadata=metadata,
        embedding=ChunkEmbedding(
            model_name="multilingual-e5-large",
            model_version=version,
            vector=vector,
        ),
    )


def test_hybrid_search_combines_semantic_text_and_metadata_filters() -> None:
    repository = InMemoryQdrantRetrievalRepository()
    service = HybridRetrievalService(retrieval_repository=repository)

    service.index_chunks(
        [
            _chunk(
                chunk_id="chunk-a",
                content="Brandschutzwand aus Stahlbeton F90",
                vector=[0.9, 0.1, 0.0],
                metadata={"project_phase": "execution", "doc_type": "plan"},
            ),
            _chunk(
                chunk_id="chunk-b",
                content="Aufmass fuer Innenputz und Deckenflaechen",
                vector=[0.2, 0.8, 0.0],
                metadata={"project_phase": "execution", "doc_type": "report"},
            ),
        ],
    )

    hits = service.search(
        HybridSearchQuery(
            tenant_id="tenant-1",
            query_text="Brandschutz Stahlbeton",
            query_vector=[1.0, 0.0, 0.0],
            limit=5,
            metadata_filters={"doc_type": "plan"},
        ),
    )

    assert len(hits) == 1
    assert hits[0].chunk_id == "chunk-a"
    assert hits[0].source_uri.startswith("s3://docs/chunk-a.pdf")


def test_reindex_plan_targets_embedding_version() -> None:
    repository = InMemoryQdrantRetrievalRepository()
    service = HybridRetrievalService(retrieval_repository=repository)

    service.index_chunks(
        [
            _chunk(
                chunk_id="chunk-old-1",
                content="A",
                vector=[1.0, 0.0],
                metadata={},
                version="e5-v1",
            ),
            _chunk(
                chunk_id="chunk-old-2",
                content="B",
                vector=[0.9, 0.1],
                metadata={},
                version="e5-v1",
            ),
            _chunk(
                chunk_id="chunk-new",
                content="C",
                vector=[0.0, 1.0],
                metadata={},
                version="e5-v2",
            ),
        ],
    )

    reindex_plan = service.create_reindex_plan(
        tenant_id="tenant-1",
        from_embedding_version="e5-v1",
        to_embedding_version="e5-v2",
    )

    assert sorted(reindex_plan.affected_chunk_ids) == ["chunk-old-1", "chunk-old-2"]
    assert reindex_plan.to_embedding_version == "e5-v2"
