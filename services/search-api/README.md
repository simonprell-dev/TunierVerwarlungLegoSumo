# search-api

Suchschicht fuer semantische und strukturierte Dokumentabfragen mit Hybrid-Retrieval.

## Ziele

- **Trennung von Verantwortlichkeiten:** Embedding-Erzeugung bleibt ausserhalb dieses Services (z. B. im `embedding-worker`).
- **Gekapselte Datenbankgrenze:** Qdrant-Zugriff erfolgt ausschliesslich ueber ein Retrieval-Repository.
- **Fachlich benannte Query-Objekte:** Queries und Filter sind im Domain-Modell (`HybridSearchQuery`) gekapselt.

## Kernbausteine

- `HybridRetrievalService` als Anwendungsdienst mit drei Hauptfaellen:
  - `index_chunks(...)`
  - `search(...)`
  - `create_reindex_plan(...)`
- `RetrievalRepository` als Port fuer Vektor- und Hybrid-Suche.
- `InMemoryQdrantRetrievalRepository` als Qdrant-kompatible Referenzimplementierung.

## Vektor-/Payload-Schema

Pro Chunk wird ein Punkt mit stabiler `chunk_id` und Embedding-Vektor persistiert. Das Payload enthaelt:

- `tenant_id`
- `document_id`
- `section_id`
- `source_uri`
- `content`
- `metadata`
- `embedding_model`
- `embedding_version`

Damit sind semantische Suche, Volltextnaehe und Metadatenfilter in einer Hybrid-Abfrage kombinierbar.

## Hybrid-Retrieval

Die Referenzlogik kombiniert:

- **semantischen Score** via Cosine Similarity,
- **keyword-basierten Score** via Token-Overlap,
- **Metadatenfilter** ueber exakte Payload-Matches.

Gesamtscore: `0.7 * semantic + 0.3 * keyword`.

## Reindexing und Embedding-Versionierung

`create_reindex_plan(...)` liefert fuer eine `from_embedding_version` alle betroffenen `chunk_id`s eines Tenants.
So kann ein dedizierter Reindex-Worker gezielt neu embeddete Chunks mit `to_embedding_version` schreiben.
