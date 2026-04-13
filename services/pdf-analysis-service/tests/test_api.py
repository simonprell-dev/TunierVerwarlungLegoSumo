import fitz
from fastapi.testclient import TestClient

from app.main import app


def _pdf() -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "PDF analyze service")
    return doc.tobytes()


def test_analyze_endpoint_accepts_pdf() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/analyze",
        files={"file": ("sample.pdf", _pdf(), "application/pdf")},
        data={"document_id": "doc-abc"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == "1.0.0"
    assert payload["document_id"] == "doc-abc"


def test_analyze_endpoint_rejects_non_pdf() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/analyze",
        files={"file": ("sample.txt", b"not-a-pdf", "text/plain")},
    )

    assert response.status_code == 400
