# BauDoc Atlas Monorepo

Monorepo-Grundgerüst für die modulare Plattform **BauDoc Atlas** (PDF → JSON, semantische Suche, LLM-Workflows, Adminoberfläche, Monitoring).

## Ziel der Struktur
Dieses Repository bildet die Grundlage für:
- saubere Trennung von Apps, Services, Workern, Shared Packages und Infrastruktur,
- einheitliche Entwicklungsstandards,
- skalierbare Zusammenarbeit in einem Multi-Team-Setup.

## Monorepo-Struktur
```text
.
├── apps/
│   ├── web/
│   └── admin/
├── services/
│   ├── api-gateway/
│   ├── auth-service/
│   ├── document-api/
│   ├── search-api/
│   ├── llm-orchestrator/
│   └── pdf-analysis-service/
├── workers/
│   ├── ingestion-worker/
│   ├── embedding-worker/
│   └── reindex-worker/
├── packages/
│   ├── shared-types/
│   ├── config/
│   └── ui/
├── infra/
│   ├── docker/
│   ├── k8s/
│   ├── observability/
│   └── scripts/
├── docs/
│   ├── adr/
│   ├── runbooks/
│   ├── standards/
│   ├── BAU-6-monorepo-struktur-standards-und-basis-dokumentation.md
│   └── BAU-8-zielarchitektur-und-skalierungsmodell.md
├── CONTRIBUTING.md
├── .editorconfig
└── .gitignore
```

## Dokumentation
- [BAU-6: Monorepo-Struktur, Entwicklungsstandards und Basis-Dokumentation](docs/BAU-6-monorepo-struktur-standards-und-basis-dokumentation.md)
- [BAU-8: Zielarchitektur und Skalierungsmodell](docs/BAU-8-zielarchitektur-und-skalierungsmodell.md)
- [BAU-10: Identität, Authentifizierung, Autorisierung und Multiuser-Grundlagen](docs/BAU-10-identitaet-authentifizierung-autorisierung-multiuser-grundlagen.md)
- [BAU-13: Queueing, Job-Orchestrierung und idempotente Verarbeitungsabläufe](docs/BAU-13-queueing-job-orchestrierung-idempotente-verarbeitungsablaeufe.md)
- [Entwicklungsstandards (Detail)](docs/standards/development-standards.md)
- [ADR-Template](docs/adr/0000-template.md)
