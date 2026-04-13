from typing import Protocol


class QueueAdapter(Protocol):
    def is_ready(self) -> bool:
        ...


class PlaceholderQueueAdapter:
    def is_ready(self) -> bool:
        return True
