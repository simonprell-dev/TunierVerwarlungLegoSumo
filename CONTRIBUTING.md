# Contributing

## Branching
- `main` bleibt stabil und releasbar.
- Feature-Arbeit erfolgt in kurzen Branches mit Bezug auf Linear-Issue (z. B. `bau-6-monorepo-setup`).

## Commit-Standard
Wir verwenden **Conventional Commits**:
- `feat:` neue Funktionalität
- `fix:` Bugfix
- `docs:` Dokumentation
- `refactor:` interne Umstrukturierung ohne Funktionsänderung
- `chore:` Build/Tooling/Housekeeping

Beispiel:
```bash
git commit -m "docs(bau-6): define monorepo baseline and standards"
```

## Pull Requests
- Kleine, fokussierte Änderungen.
- Jede PR referenziert die zugehörige Linear-ID (z. B. `BAU-6`).
- Änderungen an Architekturentscheidungen dokumentieren wir als ADR unter `docs/adr/`.
- Für neue Services muss mindestens ein lokaler Start-/Testweg dokumentiert sein.

## Qualitätssicherung (Mindestanforderung)
Vor dem Merge:
1. Linting/Formatierung für betroffene Komponenten ausführen.
2. Relevante Unit-/Integrationstests ausführen.
3. Dokumentation aktualisieren (README, Runbook, ADR falls nötig).

## Security & Secrets
- Keine Secrets im Repository.
- Lokale Konfiguration über `.env.example` + persönliche `.env`.
- Abhängigkeiten nur aus vertrauenswürdigen Quellen und möglichst mit Lockfiles.
