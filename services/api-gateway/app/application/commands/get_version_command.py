from dataclasses import dataclass


@dataclass(frozen=True)
class GetVersionCommand:
    service: str
    version: str
    api_version: str
