# HawkWatch

An incident-review assistant for uploaded security footage. Specialised computer-vision models flag *candidate* intervals (possible fights, visible fire/smoke, falls); a human reviewer confirms or dismisses each one.

Inspired by the [TreeHacks 2025 HawkWatch project](https://github.com/nf-projects/Hawkwatch), rebuilt with fine-tuned models, asynchronous inference, and an independently scalable backend.

> **Scope.** HawkWatch describes observable events; it does not accuse anyone of a crime. There is no face recognition, identity tracking, or automated dispatch. Use only footage you are authorised to process.

## Layout

| Path | What lives there |
| --- | --- |
| `web/` | Next.js dashboard: upload, job progress, incident timeline, review controls |
| `api/` | FastAPI service: signed uploads, job records, incidents, reviews |
| `worker/` | Python inference worker: leases jobs, runs models, writes incidents |
| `ml/` | Dataset manifests, training and evaluation code per incident type |
| `experiments/` | One-off scripts (e.g. the first YOLO26n benchmark) |
| `infra/` | `compose.yaml` for local dev; `aws/` for staging/production |
| `tests/load/` | Load tests for the scale demo |
| `tasks/` | [Plan](tasks/plan.md) and [build checklist](tasks/todo.md) |
| `docs/` | Architecture notes and decision records |

## Architecture

```
Browser ──signed URL──▶ Object storage (MinIO locally / S3)
   │
   ▼
Next.js ──▶ FastAPI (×2 behind a load balancer) ──▶ PostgreSQL (jobs, incidents, reviews)
                                                        │
                                   leased job queue ◀───┘   (SQS via outbox on AWS)
                                          │
                                          ▼
                                 GPU worker(s): YOLO26 · VideoMAE · pose
```

See [docs/architecture.md](docs/architecture.md).

## Quick start (local)

Requires Docker, Node 20+, Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env
docker compose -f infra/compose.yaml up -d   # postgres + minio
cd api && uv sync && uv run alembic upgrade head && uv run fastapi dev app/main.py
cd worker && uv sync && uv run python -m worker
cd web && npm install && npm run dev
```

First milestone: run the pretrained detector on a short clip.

```bash
cd experiments && uv run --with ultralytics python run_yolo.py path/to/clip.mp4
```

## Datasets

Datasets are **never committed**. Download them into `data/` (git-ignored) and record provenance and usage terms in `ml/data/manifests/` before training. See [ml/README.md](ml/README.md).

| Dataset | Use | Notes |
| --- | --- | --- |
| RWF-2000 | Fight clip classification | Non-commercial; no redistribution |
| D-Fire | Fire/smoke detection | Check component licences |
| UR Fall | Fall detection pilot | Small; benchmark only |
| UCF-Crime | Later: temporal localisation | Disturbing content; controlled subset |
