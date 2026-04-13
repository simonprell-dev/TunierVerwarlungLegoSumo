from pathlib import Path

from app.domain.ports.storage import FileStoragePort, StoredFile


class LocalFileStorageAdapter(FileStoragePort):
    def __init__(self, base_dir: str) -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, *, tenant_id: str, document_id: str, filename: str, content: bytes) -> StoredFile:
        target_dir = self._base_dir / tenant_id / document_id
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / filename
        target_path.write_bytes(content)

        return StoredFile(storage_path=str(target_path), size_bytes=len(content))
