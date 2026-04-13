from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_document_registers_metadata_and_job() -> None:
    tenant_id = str(uuid4())
    owner_user_id = str(uuid4())

    response = client.post(
        "/v1/uploads/documents",
        data={
            "tenant_id": tenant_id,
            "owner_user_id": owner_user_id,
            "title": "Bauplan Q2",
        },
        files={"document": ("bauplan.pdf", b"%PDF-1.4 test", "application/pdf")},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["document_id"]
    assert payload["job_id"]
    assert payload["status"] == "registered"
    assert payload["filename"] == "bauplan.pdf"


def test_duplicate_upload_detected_by_checksum() -> None:
    tenant_id = str(uuid4())
    owner_user_id = str(uuid4())
    file_payload = ("spec.txt", b"same-content", "text/plain")

    first_response = client.post(
        "/v1/uploads/documents",
        data={"tenant_id": tenant_id, "owner_user_id": owner_user_id},
        files={"document": file_payload},
    )
    second_response = client.post(
        "/v1/uploads/documents",
        data={"tenant_id": tenant_id, "owner_user_id": owner_user_id},
        files={"document": file_payload},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    first_payload = first_response.json()
    second_payload = second_response.json()
    assert second_payload["status"] == "duplicate"
    assert second_payload["document_id"] == first_payload["document_id"]
    assert second_payload["job_id"] is None
