# Entwicklungsstandards

## 1. Ziel
Diese Standards vereinheitlichen die tägliche Entwicklung im BauDoc-Atlas-Monorepo.

## 2. Repository-Konventionen
- Monorepo mit klarer Trennung nach `apps/`, `services/`, `workers/`, `packages/`, `infra/` und `docs/`.
- Jede neue Komponente erhält ein eigenes Unterverzeichnis mit README.
- Cross-Cutting-Code wird in `packages/` abgelegt.

## 3. Branching & Commits
- Branch-Namen enthalten die Ticket-ID (`bau-<id>-kurzbeschreibung`).
- Commit-Konvention: Conventional Commits.
- Squash-Merge bevorzugt, um Historie fokussiert zu halten.

## 4. Code-Qualität
- Linting und Formatierung sind verpflichtend vor Merge.
- Tests mindestens auf betroffener Ebene (unit/integration).
- Keine toten Features ohne Dokumentation oder Deaktivierungsstrategie.

## 5. Dokumentation
- Architekturentscheidungen als ADR in `docs/adr/`.
- Betrieblich relevante Schritte als Runbook in `docs/runbooks/`.
- Änderungen mit Auswirkungen auf Dev-Workflow müssen `README.md` und/oder `CONTRIBUTING.md` anpassen.

## 6. Security-Baseline
- Keine Klartext-Secrets im Repo.
- Principle of least privilege für Services und technische Nutzer.
- Abhängigkeiten regelmäßig prüfen und aktualisieren.

## 7. Definition of Done (DoD)
Ein Task ist abgeschlossen, wenn:
1. Code/Struktur implementiert ist,
2. relevante Tests/Checks erfolgreich waren,
3. notwendige Dokumentation aktualisiert wurde,
4. PR nachvollziehbar beschreibt, warum die Änderung nötig ist.
