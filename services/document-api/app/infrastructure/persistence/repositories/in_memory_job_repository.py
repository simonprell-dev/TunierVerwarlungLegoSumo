from app.application.dtos import JobPersistenceDTO
from app.domain.ports.repositories import JobRepository


class InMemoryJobRepository(JobRepository):
    def __init__(self) -> None:
        self.jobs: dict[str, JobPersistenceDTO] = {}

    def upsert_job(self, dto: JobPersistenceDTO) -> None:
        self.jobs[str(dto.id)] = dto
