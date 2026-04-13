from dataclasses import dataclass


@dataclass(frozen=True)
class StoredFile:
    storage_path: str
    size_bytes: int


class FileStoragePort:
    def save(self, *, tenant_id: str, document_id: str, filename: str, content: bytes) -> StoredFile:
        ...
