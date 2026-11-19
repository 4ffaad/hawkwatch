# Architecture

## Upload and processing sequence

```mermaid
sequenceDiagram
    autonumber
    actor R as Reviewer
    participant W as Dashboard
    participant A as FastAPI
    participant S as Object storage
    participant P as PostgreSQL
    participant K as Worker

    R->>W: choose video
    W->>A: POST /uploads (name, size, type)
    A->>P: insert video (pending)
    A-->>W: signed PUT URL
    W->>S: PUT video bytes (direct)
    W->>A: POST /uploads/{id}/complete
    A->>S: HEAD object (size, ETag)
    A->>P: video → uploaded + insert job (queued), one transaction
    A-->>W: job id
    loop every few seconds
        K->>P: lease next job (SKIP LOCKED)
    end
    K->>S: download video
    K->>K: clips → models → intervals
    K->>P: insert incidents + job → completed (if lease held)
    W->>A: GET /jobs/{id}, /incidents (polling)
    R->>W: confirm / dismiss
    W->>A: POST /incidents/{id}/review
    A->>P: insert review
```

## Data model

```mermaid
erDiagram
    VIDEOS ||--o{ JOBS : "processed by"
    JOBS ||--o{ INCIDENTS : produces
    INCIDENTS ||--o{ REVIEWS : "reviewed in"
    VIDEOS {
        uuid id PK
        string owner_id
        string object_key
        string object_etag
        enum status "pending | uploaded"
    }
    JOBS {
        uuid id PK
        uuid video_id FK
        enum status "queued | running | completed | failed"
        int attempts
        uuid lease_token
        timestamp lease_until
    }
    INCIDENTS {
        uuid id PK
        uuid job_id FK
        enum category
        int start_ms
        int end_ms
        float score
        string model_version
    }
    REVIEWS {
        uuid id PK
        uuid incident_id FK
        string reviewer_id
        enum decision "confirmed | dismissed"
    }
```

## Request flow

1. The dashboard calls `POST /uploads` with filename, size and content type. The API creates a `videos` row (`pending`) and returns a short-lived signed `PUT` URL.
2. The browser uploads directly to private object storage. Video bytes never pass through the API.
3. The dashboard calls `POST /uploads/{id}/complete`. The API `HEAD`s the object, checks size and owner, records its ETag/version, and in the **same transaction** inserts a `jobs` row (`queued`).
4. A worker leases a job (`SELECT … FOR UPDATE SKIP LOCKED`, sets `lease_until`), renews the lease while running, and writes incidents.
5. The dashboard polls `GET /jobs/{id}` and `GET /jobs/{id}/incidents`; the reviewer posts a decision to `POST /incidents/{id}/review`.

## Delivery guarantees

- **At-least-once processing.** A crashed worker's lease expires and another worker picks the job up. `attempts` is bounded by `WORKER_MAX_ATTEMPTS`; then the job is `failed`.
- **Exactly-once results.** Incidents carry a unique key `(job_id, category, start_ms)` and are written in one transaction with the job's `completed` transition, guarded by the lease token. A stale worker's commit is rejected.
- **Immutable input.** Each job pins the object key and ETag verified at step 3.

## Scaling (AWS)

| Component | Local | AWS | Scales on |
| --- | --- | --- | --- |
| API | `fastapi dev` | ECS Fargate ×2 behind ALB | CPU / request count |
| Queue | Postgres leases | SQS + DLQ, published via outbox table | — |
| Worker | `python -m worker` | ECS on EC2 GPU | SQS backlog per task, oldest message age |
| Storage | MinIO | S3 (private, SSE) | — |
| DB | Postgres 17 | RDS Postgres | — |
| Cache | — | ElastiCache Redis, only once read load is measured | — |

## Responsible-use constraints

- Outputs are *candidates* for human review, worded as observable events.
- No face recognition, identity linking, or automated dispatch.
- Evidence access is scoped to the uploading organisation and audited; retention is configurable and deletion is tested.
