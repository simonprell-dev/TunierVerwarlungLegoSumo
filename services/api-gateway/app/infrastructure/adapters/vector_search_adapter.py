from typing import Protocol


class VectorSearchAdapter(Protocol):
    def is_ready(self) -> bool:
        ...


class PlaceholderVectorSearchAdapter:
    def is_ready(self) -> bool:
        return True
