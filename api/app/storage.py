from functools import lru_cache

import boto3
from botocore.client import Config

from app.config import get_settings


@lru_cache
def s3():
    s = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=s.s3_endpoint_url,
        region_name=s.aws_region,
        aws_access_key_id=s.aws_access_key_id,
        aws_secret_access_key=s.aws_secret_access_key,
        config=Config(signature_version="s3v4"),
    )


def presign_put(key: str, content_type: str) -> str:
    s = get_settings()
    return s3().generate_presigned_url(
        "put_object",
        Params={"Bucket": s.s3_bucket, "Key": key, "ContentType": content_type},
        ExpiresIn=s.signed_url_ttl_seconds,
    )


def presign_get(key: str) -> str:
    s = get_settings()
    return s3().generate_presigned_url(
        "get_object", Params={"Bucket": s.s3_bucket, "Key": key}, ExpiresIn=s.signed_url_ttl_seconds
    )


def head(key: str) -> dict | None:
    try:
        return s3().head_object(Bucket=get_settings().s3_bucket, Key=key)
    except s3().exceptions.ClientError:
        return None
