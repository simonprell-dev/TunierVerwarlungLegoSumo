# BAU-8 · Zielarchitektur und Skalierungsmodell

## 1) Zielbild
Eine modularisierte, containerisierte Plattform für Baudokumente mit folgenden End-to-End-Fähigkeiten:

1. Upload und Verwaltung von PDFs/Dokumenten.
2. Asynchrone Verarbeitung (`PDF -> strukturierte Inhalte/JSON`).
3. Semantische Suche über Embeddings und Metadatenfilter.
4. LLM-gestützte Q&A-/Assistenz-Workflows auf Dokumentbasis.
5. Multiuser-Webfrontend mit Rollen/Rechte-Modell.
6. Adminoberfläche für Betrieb, Korrekturen, Re-Indexing und Nutzerverwaltung.
7. Beobachtbarkeit (Logs, Metriken, Traces), Backups und Recovery.

## 2) Architekturprinzipien
- **Container-first**: Jeder fachliche Baustein als eigener Dienst.
- **Asynchron vor synchron**: Rechenintensive Verarbeitung über Queue/Worker entkoppeln.
- **Datenhoheit lokal/on-prem-fähig**: Primär self-hosted, cloud-kompatibel.
- **Skalierung entlang Engpässen**: API, Worker, Vektorsuche und LLM-Runtime separat skalieren.
- **Security by default**: TLS, Secret-Management, least privilege, Audit-Logs.
- **AI austauschbar**: Modell-/Provider-Layer abstrahieren (lokal vs. extern).

## 3) Zielarchitektur (Container/Module)

### 3.1 Entry & User Experience
- **Webfrontend** (Multiuser): React/Vue/Svelte o.ä., rollenbasiertes UI.
- **Admin-Frontend**: Betriebs- und Korrektur-Workflows (Ingestion, Jobs, Nutzer, Mandanten).
- **API Gateway / Reverse Proxy**: TLS-Termination, Routing, Rate Limits, Auth-Forwarding.

### 3.2 Core Backend
- **Auth-Service**: OIDC/OAuth2, Rollen (Admin, Editor, Reader, Service).
- **Document API**: Upload, Versionierung, Metadaten, Dokumentzustand.
- **Search API**: Hybridsuche (semantisch + keyword/filter), Ranking, Snippets.
- **LLM Orchestrator**: Prompting, Retrieval, Kontextfenster, Guardrails, Caching.

### 3.3 Ingestion & AI Pipeline
- **Ingestion Worker**: PDF Parsing, OCR-Anstoß, Chunking, Strukturierung.
- **Extraction Service**: Regeln/Modelle für `PDF -> JSON` inkl. Feldnormalisierung.
- **Embedding Worker**: Embedding-Generierung für Text-Chunks.
- **Reindex/Reprocess Worker**: Batch-Neuberechnung bei Modell- oder Schemawechsel.

### 3.4 Data Layer
- **Relationale DB** (PostgreSQL): Nutzer, Rechte, Dokument-Metadaten, Job-Status, Audit.
- **Object Storage** (S3-kompatibel/MinIO): Originale, Derivate, OCR-Artefakte.
- **Vector Store** (pgvector, Qdrant oder Weaviate): Embeddings + Referenzen.
- **Cache** (Redis): Sessions, Rate-Limits, LLM-Result-Caching, Queue-Broker.

### 3.5 Operations
- **Queue/Broker** (Redis Streams/RabbitMQ/NATS): Entkopplung API ↔ Worker.
- **Monitoring Stack**: Prometheus + Grafana, zentralisierte Logs (z. B. Loki/ELK), OpenTelemetry.
- **Backup/Restore Jobs**: DB-Dumps, Object Storage Versioning, Restore-Prozeduren.

## 4) Referenz-Datenfluss
1. User lädt PDF hoch (Frontend -> Gateway -> Document API).
2. Document API speichert Datei im Object Storage, Metadaten in PostgreSQL.
3. Event/Job wird in Queue eingestellt.
4. Ingestion Worker verarbeitet PDF, erstellt Chunks und strukturierte JSON-Daten.
5. Embedding Worker erzeugt Vektoren, speichert diese im Vector Store.
6. Search API und LLM Orchestrator greifen auf Metadaten + Vektoren + Inhalte zu.
7. Admin sieht Pipeline-Status, kann fehlerhafte Jobs neu starten.

## 5) Skalierungsmodell

### 5.1 Horizontale Skalierung nach Lastprofil
- **API-Tier**: stateless -> Replikate hoch/runter (z. B. 2..N).
- **Worker-Tier**: autoskalieren nach Queue-Länge, Durchlaufzeit und GPU/CPU-Auslastung.
- **Vector Store**: Sharding/Replikation abhängig von Vektoranzahl und Query-Latenz.
- **LLM Runtime**: dedizierte Inference-Knoten (GPU), getrennt von API/Worker.

### 5.2 Vertikale Skalierung für Speziallasten
- OCR/Parsing häufig CPU-/RAM-lastig.
- Embeddings/LLM je nach Modell GPU-lastig.
- Empfehlung: Workloads via Node Labels/Taints separieren (CPU-Pool, GPU-Pool).

### 5.3 Skalierungsstufen (Target)
- **Stufe S (Pilot)**
  - 100–5.000 Dokumente
  - 1–20 gleichzeitige Nutzer
  - 1 Worker-Pool (CPU), optional 1 kleiner GPU-Runner
- **Stufe M (Betrieb)**
  - 5.000–100.000 Dokumente
  - 20–200 gleichzeitige Nutzer
  - getrennte Pools: API, OCR/Extraction, Embeddings, LLM
- **Stufe L (Enterprise)**
  - >100.000 Dokumente, Mandantenbetrieb
  - >200 gleichzeitige Nutzer
  - dedizierte Cluster/Namespaces pro Domäne oder Mandant, HA für DB/Vector/Broker

## 6) Deployment-Modell
- **Phase 1**: Docker Compose (lokale Integration, schnelle Iteration).
- **Phase 2**: Kubernetes (k3s/k8s), Helm/ArgoCD für deklarative Deployments.
- **Phase 3**: Produktions-Härtung mit HA, Blue/Green oder Canary, SLO-basiertes Autoscaling.

## 7) Sicherheit & Governance
- Zentrale Authentifizierung (OIDC), RBAC bis auf Dokument-/Mandantenebene.
- End-to-End TLS (intern + extern), Secret-Management (z. B. Vault/Sealed Secrets).
- Audit-Log für Upload, Suche, Exporte, Adminaktionen.
- Datenklassifizierung + Aufbewahrungsregeln + Löschkonzepte.

## 8) Betriebsmetriken (MVP)
- Upload -> indexierbar (P95) in Minuten.
- Suche-Latenz (P95/P99).
- Antwortqualität (retrieval hit rate / citation coverage).
- Fehlerrate pro Pipeline-Schritt.
- Kosten pro 1.000 Dokumentseiten (CPU/GPU/Storage).

## 9) Risiken & Gegenmaßnahmen
- **OCR-Qualität schwankt** -> Qualitäts-Scoring + manuelle Korrekturschleife.
- **LLM-Halluzinationen** -> RAG with citations, confidence thresholds, fallback answers.
- **Kostenexplosion bei Embeddings/Inference** -> Caching, batching, Modellklassen pro Use Case.
- **Schema-/Modellwechsel** -> versionierte Pipelines + Reindex-Jobs.

## 10) Ergebnis für BAU-8
Mit dieser Zielarchitektur ist die Plattform
- modular erweiterbar,
- auf CPU/GPU-Lastspitzen gezielt skalierbar,
- betrieblich überwachbar,
- und für den Übergang von Pilot zu produktivem Multiuser-Betrieb vorbereitet.

Nächste sinnvolle Folgeaufgaben:
1. BAU-9: Zieltechnologie-Stack (konkrete Auswahl je Modul inkl. ADRs).
2. BAU-10: Betriebs-SLOs und Kapazitätsplanung je Skalierungsstufe.
3. BAU-11: Sicherheits- und Rollenmodell detaillieren.
