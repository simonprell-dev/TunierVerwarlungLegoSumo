from collections.abc import Callable

from app.application.dtos import JobPersistenceDTO
from app.domain.ports.repositories import JobRepository

SqlExecutor = Callable[[str, dict], None]


class PostgresJobRepository(JobRepository):
    def __init__(self, execute: SqlExecutor) -> None:
        self._execute = execute

    def upsert_job(self, dto: JobPersistenceDTO) -> None:
        self._execute(
            """
            INSERT INTO processing_jobs (
                id, tenant_id, document_id, job_type, status, requested_by_user_id,
                payload, result_payload, error_payload, attempts, max_attempts,
                scheduled_at, started_at, finished_at, created_at, updated_at
            ) VALUES (
                %(id)s, %(tenant_id)s, %(document_id)s, %(job_type)s, %(status)s,
                %(requested_by_user_id)s, %(payload)s::jsonb, %(result_payload)s::jsonb,
                %(error_payload)s::jsonb, %(attempts)s, %(max_attempts)s,
                %(scheduled_at)s, %(started_at)s, %(finished_at)s, %(created_at)s,
                %(updated_at)s
            )
            ON CONFLICT (id) DO UPDATE SET
                status = EXCLUDED.status,
                result_payload = EXCLUDED.result_payload,
                error_payload = EXCLUDED.error_payload,
                attempts = EXCLUDED.attempts,
                started_at = EXCLUDED.started_at,
                finished_at = EXCLUDED.finished_at,
                updated_at = EXCLUDED.updated_at
            """,
            dto.__dict__,
        )
