from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: str
    job_id: str | None
    filename: str
    checksum_sha256: str
    storage_path: str
    status: str
