from typing import Protocol


class DatabaseAdapter(Protocol):
    def is_ready(self) -> bool:
        ...


class PlaceholderDatabaseAdapter:
    def is_ready(self) -> bool:
        return True
