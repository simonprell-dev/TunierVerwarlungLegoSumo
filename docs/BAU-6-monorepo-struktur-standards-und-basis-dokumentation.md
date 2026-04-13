# BAU-6 · Monorepo Struktur, Entwicklungsstandards und Basis-Dokumentation

## 1) Ergebnisübersicht
Für BAU-6 wurden folgende Grundlagen geschaffen:
1. Monorepo-Ordnerstruktur für Apps, Services, Worker, Shared Packages und Infrastruktur.
2. Teamweite Basiskonventionen für Branching, Commits, Reviews und Dokumentation.
3. Dokumentationsgrundlagen mit Standards, ADR-Template und Runbook-Platzhaltern.

## 2) Strukturprinzipien
- **Domänenbasiert statt technologiegetrieben**: Jede fachliche Einheit erhält ihren klaren Ort.
- **Gemeinsam nutzbarer Kern**: `packages/` für Typen, Config und UI-Bausteine.
- **Ops als First-Class Citizen**: Infrastruktur und Observability unter `infra/`.
- **Docs-as-Code**: Standards und Entscheidungen liegen versioniert im Repo.

## 3) Ownership-Vorschlag
- `apps/`: Produktteam Frontend
- `services/`: Backend-Team
- `workers/`: AI/Processing-Team
- `packages/`: Plattform-Team (in enger Abstimmung mit Feature-Teams)
- `infra/`: Platform/DevOps
- `docs/`: gemeinschaftliche Pflege; ADRs mit klarer Decision Owner:in

## 4) Entwicklungsstandards (Kurzfassung)
- Branches pro Arbeitspaket (Linear-Referenz).
- Conventional Commits.
- Pflicht zur Dokumentationsaktualisierung bei Struktur-/Architekturänderungen.
- ADR bei technischen Richtungsentscheidungen.
- Keine Secrets im Git.

## 5) Definition of Ready (DoR) für neue Module
Ein neues Modul (Service/Worker/App) gilt als "ready", wenn:
1. Verzeichnisstruktur angelegt ist,
2. README (Zweck, Schnittstellen, lokale Ausführung) existiert,
3. Basis-Lint/Test-Setup dokumentiert ist,
4. Deploymentpfad (`infra/docker` oder `infra/k8s`) beschrieben ist,
5. Ownership/Verantwortung geklärt ist.

## 6) Nächste sinnvolle Schritte
1. Workspace-Tooling festlegen (z. B. pnpm + turbo oder nx) und bootstrappen.
2. Service-Templates mit einheitlicher CI-Pipeline ergänzen.
3. CODEOWNERS und Branch-Protection-Regeln einführen.
