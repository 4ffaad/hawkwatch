import socket

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    database_url: str = "postgresql+psycopg://hawkwatch:hawkwatch@localhost:5432/hawkwatch"
    s3_endpoint_url: str | None = "http://localhost:9000"
    s3_bucket: str = "hawkwatch-videos"
    aws_region: str = "us-east-1"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    worker_id: str = socket.gethostname()
    worker_lease_seconds: int = 120
    worker_max_attempts: int = 3
    worker_poll_seconds: float = 2.0
    worker_device: str = "cpu"  # cpu | mps | cuda


settings = Settings()
