# pdf-analysis-service

Eigenständiger Service zur PDF-Analyse (Layout + OCR) mit klar versioniertem Ausgabeschema.

## Fokus des Services
- analysiert PDF-Rohdokumente
- extrahiert Seiten, Textblöcke und Tabellen
- ergänzt OCR-Fallback für Seiten ohne eingebetteten Text
- liefert Fehler- und Qualitätskennzeichen

Nicht enthalten (bewusst): Vorverarbeitung, Chunking, Embedding-Logik.

## API
- `GET /v1/health`
- `POST /v1/analyze` (`multipart/form-data`)
  - `file`: PDF-Datei
  - `document_id` (optional)

### Beispielantwort (gekürzt)
```json
{
  "schema_version": "1.0.0",
  "document_id": "...",
  "analyzed_at": "2026-04-13T12:00:00Z",
  "runtime": {
    "ocr_engine": "pytesseract",
    "ocr_used": false,
    "gpu_mode": false,
    "page_count": 4
  },
  "pages": [
    {
      "page_number": 1,
      "blocks": [
        {"id": "p1-b0", "source": "embedded_text", "confidence": 0.99, "text": "..."}
      ],
      "tables": [],
      "quality_flags": []
    }
  ],
  "errors": [],
  "quality_flags": []
}
```

## Local run
```bash
pip install -e .
uvicorn app.main:app --reload --port 8080
```

## Container
```bash
docker build -t baudoc/pdf-analysis-service:local .
docker run --rm -p 8080:8080 baudoc/pdf-analysis-service:local
```

## GPU / CPU Hinweis
Der Service markiert den gewünschten Betriebsmodus über `OCR_DEVICE` (`cpu`/`gpu`) in `runtime.gpu_mode`.
Die OCR-Implementierung basiert auf Tesseract (CPU). Ein GPU-Host kann über künftige OCR-Backends ergänzt werden, ohne Schemaänderung.
