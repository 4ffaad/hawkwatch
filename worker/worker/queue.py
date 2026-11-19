"""Postgres-backed job queue with renewable leases.

A job is claimed with SELECT ... FOR UPDATE SKIP LOCKED and given a fresh lease token.
Every later write is conditioned on that token, so a worker whose lease expired (and whose
job was re-claimed by someone else) cannot commit results.
"""

import uuid
from dataclasses import dataclass

from sqlalchemy import create_engine, text

from worker.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)


@dataclass(frozen=True)
class Lease:
    job_id: uuid.UUID
    token: uuid.UUID
    object_key: str
    attempt: int


class LeaseLost(Exception):
    pass


def claim() -> Lease | None:
    token = uuid.uuid4()
    with engine.begin() as conn:
        # Jobs out of attempts whose lease expired are failed, not retried.
        conn.execute(
            text(
                """
                UPDATE jobs SET status = 'failed', error = 'max attempts exceeded',
                       finished_at = now(), lease_token = NULL
                WHERE status = 'running' AND lease_until < now() AND attempts >= :max
                """
            ),
            {"max": settings.worker_max_attempts},
        )
        row = conn.execute(
            text(
                """
                WITH next AS (
                  SELECT j.id FROM jobs j
                  WHERE (j.status = 'queued')
                     OR (j.status = 'running' AND j.lease_until < now() AND j.attempts < :max)
                  ORDER BY j.created_at
                  FOR UPDATE SKIP LOCKED
                  LIMIT 1
                )
                UPDATE jobs j SET status = 'running', attempts = j.attempts + 1,
                       lease_token = :token,
                       lease_until = now() + make_interval(secs => :lease),
                       started_at = COALESCE(j.started_at, now()), error = NULL
                FROM next, videos v
                WHERE j.id = next.id AND v.id = j.video_id
                RETURNING j.id, v.object_key, j.attempts
                """
            ),
            {"token": token, "lease": settings.worker_lease_seconds, "max": settings.worker_max_attempts},
        ).first()
    if row is None:
        return None
    return Lease(job_id=row.id, token=token, object_key=row.object_key, attempt=row.attempts)


def renew(lease: Lease) -> None:
    with engine.begin() as conn:
        n = conn.execute(
            text(
                "UPDATE jobs SET lease_until = now() + make_interval(secs => :lease) "
                "WHERE id = :id AND lease_token = :token AND status = 'running'"
            ),
            {"id": lease.job_id, "token": lease.token, "lease": settings.worker_lease_seconds},
        ).rowcount
    if n != 1:
        raise LeaseLost(str(lease.job_id))


def complete(lease: Lease, incidents: list[dict]) -> None:
    """Atomically write incidents and mark the job completed, only if we still hold the lease."""
    with engine.begin() as conn:
        n = conn.execute(
            text(
                "UPDATE jobs SET status = 'completed', finished_at = now(), lease_token = NULL "
                "WHERE id = :id AND lease_token = :token AND status = 'running'"
            ),
            {"id": lease.job_id, "token": lease.token},
        ).rowcount
        if n != 1:
            raise LeaseLost(str(lease.job_id))  # rolls back; nothing is written
        for inc in incidents:
            conn.execute(
                text(
                    """
                    INSERT INTO incidents (id, job_id, category, start_ms, end_ms, score,
                                           model_version, evidence_key, summary, created_at)
                    VALUES (gen_random_uuid(), :job_id, :category, :start_ms, :end_ms, :score,
                            :model_version, :evidence_key, :summary, now())
                    ON CONFLICT (job_id, category, start_ms) DO NOTHING
                    """
                ),
                {"job_id": lease.job_id, "evidence_key": None, "summary": None, **inc},
            )


def fail(lease: Lease, error: str, retryable: bool) -> None:
    """Record an error. Retryable errors go back to the queue until attempts run out."""
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE jobs SET
                  status = CASE WHEN :retryable AND attempts < :max THEN 'queued' ELSE 'failed' END::job_status,
                  finished_at = CASE WHEN :retryable AND attempts < :max THEN NULL ELSE now() END,
                  error = :error, lease_token = NULL, lease_until = NULL
                WHERE id = :id AND lease_token = :token
                """
            ),
            {
                "id": lease.job_id,
                "token": lease.token,
                "error": error[:2000],
                "retryable": retryable,
                "max": settings.worker_max_attempts,
            },
        )
