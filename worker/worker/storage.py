import boto3

from worker.config import settings

_s3 = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint_url,
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)


def download(key: str, dest: str) -> None:
    _s3.download_file(settings.s3_bucket, key, dest)
