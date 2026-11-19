"""Create the local storage bucket. Dev only: `uv run python -m app.dev_bootstrap`."""

import time

from app.config import get_settings
from app.storage import s3


def main() -> None:
    bucket = get_settings().s3_bucket
    for _ in range(30):
        try:
            existing = {b["Name"] for b in s3().list_buckets().get("Buckets", [])}
            break
        except Exception:  # noqa: BLE001  (storage still starting)
            time.sleep(1)
    else:
        raise SystemExit("object storage not reachable")
    if bucket not in existing:
        s3().create_bucket(Bucket=bucket)
    print(f"bucket ready: {bucket}")


if __name__ == "__main__":
    main()
