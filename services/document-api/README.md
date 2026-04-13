# document-api

Persistenz-Grundlage für Dokumente, Sections, Jobs, Benutzer/Rollen und Artefakte in PostgreSQL.

## Ziele
- stabiles relationales Kernmodell für Fachobjekte
- klare JSONB-Strategie für variable PDF-Extraktionsdaten und Hilfsartefakte
- getrennte Persistenzschicht (Repository-Ports im Domain-Layer, SQL nur in Infrastruktur)
- reproduzierbare, idempotente Migrationen inklusive Rollback-Skript

## Struktur
```text
app/
├── application/
│   └── dtos.py                                        # Value Objects/DTOs für Persistenz
├── domain/
│   └── ports/
│       └── repositories.py                            # Repository-Boundary (Ports)
└── infrastructure/
    └── persistence/
        ├── migrations/
        │   ├── 0001_init_schema.up.sql               # idempotente Initialmigration
        │   └── 0001_init_schema.down.sql             # Rollback
        └── repositories/
            ├── postgres_document_repository.py        # SQL für Dokumente + Sections
            └── postgres_job_repository.py             # SQL für Jobs
```

## Datenmodell (Kurzüberblick)
- `app_users`, `roles`, `user_roles` für Benutzer und Autorisierung.
- `documents` mit Version (`version`) und Status (`status`) für Verarbeitungszustände.
- `document_sections` für strukturierte Dokumentabschnitte.
- `processing_jobs` für asynchrone Verarbeitung (inkl. Retry-Felder).
- `artifacts` für Hilfsdateien (z. B. OCR-Ausgaben, abgeleitete JSON-Dateien, Preview-Dateien).

## JSONB-Nutzung
- `documents.processing_state`: technischer Workflow-Zustand (z. B. Stage, Flags).
- `documents.extracted_pdf_data`: extrahierte PDF-Informationen mit variabler Struktur.
- `documents.metadata`, `document_sections.metadata`, `artifacts.metadata`: flexible Fach-Metadaten.
- `artifacts.auxiliary_data`: zusätzliche Artefaktdaten.
- `processing_jobs.payload/result_payload/error_payload`: Job-Input/Output/Fehlerkontext.

Alle JSONB-Felder erhalten Defaultwerte (`'{}'::jsonb`) und gezielte GIN-Indizes für Suchzugriffe.

## Migrationen anwenden
```bash
psql "$DATABASE_URL" -f app/infrastructure/persistence/migrations/0001_init_schema.up.sql
```

## Rollback
```bash
psql "$DATABASE_URL" -f app/infrastructure/persistence/migrations/0001_init_schema.down.sql
```

Rollback ist bewusst explizit als separates Skript geführt, um in Betriebsabläufen kontrolliert auszurollen.
