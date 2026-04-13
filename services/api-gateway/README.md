# API Gateway

Backend-Grundgerüst für BauDoc Atlas mit klarer Trennung zwischen API, Application-, Domain- und Infrastruktur-Schicht.

## Ziele dieses Grundgerüsts
- konsistentes Routing über versionierte Endpunkte (`/v1/...`)
- standardisierte Fehlerantworten für Validierung und Serverfehler
- vorbereitete Adapter-Schnittstellen für Datenbank, Queue, Vektorsuche und Modellzugriff
- strikte Trennung von Endpunkten und fachlicher Logik

## Struktur
```text
app/
├── api/
│   ├── routes/         # HTTP-Endpunkte
│   └── schemas/        # DTOs für Request/Response
├── application/
│   ├── commands/       # Commands als Input für Use-Cases
│   └── services/       # Use-Case-Logik
├── domain/
│   └── services/       # fachliche Kernlogik
├── infrastructure/
│   └── adapters/       # Ports/Adapter für externe Systeme
└── core/               # Versionierung, globale Fehlerbehandlung
```

## Basis-Endpunkte
- `GET /` -> Dienststatus
- `GET /v1/health` -> Health-Check
- `GET /v1/version` -> Service- und API-Version

## Starten
```bash
cd services/api-gateway
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload --port 8080
```

## Tests
```bash
cd services/api-gateway
pytest
```
