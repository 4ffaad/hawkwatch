# HawkWatch

An incident-review assistant for uploaded security footage. Models flag *candidate* time ranges (possible fight, fire/smoke, fall); a human confirms or dismisses each one. This is an original project built from scratch. Describe it that way in docs and commits.

The owner is still learning the codebase. Explain things plainly, point to specific files and lines, and prefer small, readable changes over clever ones.

## How it fits together

1. The dashboard (`web/`) asks the API for a signed URL and uploads the video straight to object storage.
2. The API (`api/`) checks the upload exists and creates a `queued` job in Postgres.
3. A worker (`worker/`) leases the job, cuts the video into 2-second clips, runs the detectors, merges flagged clips into intervals and writes incidents.
4. The reviewer confirms or dismisses incidents in the dashboard.

API and workers scale separately. Diagrams are in `README.md` and `docs/architecture.md`.

## Status

- Upload → queue → worker → review works end to end.
- No trained models yet. Jobs finish with "No candidates found". Next step: train the fight model (`ml/fight/train.py` is a stub). See `tasks/todo.md`.
- Auth is a dev stub (`X-User-Id` header in `api/app/auth.py`) and must be replaced before anything is public.

## Reading order (the files that matter)

1. `api/app/models.py`: tables (videos, jobs, incidents, reviews)
2. `api/app/routers/uploads.py`: upload → job
3. `worker/worker/__main__.py`: worker loop
4. `worker/worker/pipeline.py`, `video.py`, `intervals.py`: clips → detectors → intervals
5. `api/app/routers/jobs.py`: results and review endpoints
6. `web/src/app/jobs/[id]/job-view.tsx`: review page
7. `worker/worker/queue.py`: leases, retries, no-duplicate guarantees (hardest file)

Mostly config, so skip unless needed: `pyproject.toml`, `alembic.ini`, `migrations/`, `config.py`, `db.py`, Dockerfiles, `infra/`, `.github/`.

## Running locally

```bash
docker compose -f infra/compose.yaml start        # first time: `up -d`, then in api/: uv run python -m app.dev_bootstrap && uv run alembic upgrade head
cd api && uv run fastapi dev app/main.py          # http://localhost:8000/docs
cd worker && uv run python -m worker
cd web && npm run dev                             # http://localhost:3000
```

Checks (same as CI): `uv run ruff check . && uv run pytest` in `api/` and `worker/`; `npm run lint && npm run build` in `web/`.

Local storage is SeaweedFS (S3-compatible) on port 9000; credentials are in `.env` (copied from `.env.example`).

## Rules

- Never commit datasets, videos, model weights or `.env`. `data/`, `models/`, `runs/` and `graphify-out/` are git-ignored. Demo clips in `data/demo/` are for local testing only.
- Datasets need a provenance/licence manifest in `ml/data/manifests/` before training.
- Responsible use: describe observable events only, never accuse. No face recognition, identity tracking or automated dispatch.
- Don't commit or push unless the owner asks.
- `web/` uses Next.js 16. Read `web/AGENTS.md` before changing it.
