# GPU image for ECS on EC2. For local CPU/MPS runs use `uv run python -m worker` directly.
FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libgl1 && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --extra models
COPY . .
ENV WORKER_DEVICE=cuda
CMD ["uv", "run", "--no-dev", "python", "-m", "worker"]
