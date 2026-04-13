from dataclasses import dataclass


@dataclass(frozen=True)
class HealthState:
    status: str
    service_name: str


class HealthService:
    def check(self, service_name: str) -> HealthState:
        return HealthState(status="ok", service_name=service_name)
