from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    database_url: str = "postgresql+psycopg://hawkwatch:hawkwatch@localhost:5432/hawkwatch"
    s3_endpoint_url: str | None = "http://localhost:9000"
    s3_bucket: str = "hawkwatch-videos"
    aws_region: str = "us-east-1"
    # Leave unset on AWS to use the task role; set for local S3-compatible storage.
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    max_upload_bytes: int = 500 * 1024 * 1024
    signed_url_ttl_seconds: int = 900
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
