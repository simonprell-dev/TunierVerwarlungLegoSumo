from typing import Protocol


class ModelAdapter(Protocol):
    def is_ready(self) -> bool:
        ...


class PlaceholderModelAdapter:
    def is_ready(self) -> bool:
        return True
