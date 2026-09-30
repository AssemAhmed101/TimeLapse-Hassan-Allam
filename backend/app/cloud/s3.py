from pathlib import Path

from app.cloud.base import CloudStorageError, CloudStorageProvider


class S3CloudProvider(CloudStorageProvider):
    def __init__(
        self,
        *,
        bucket: str,
        region: str | None = None,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
    ):
        try:
            import boto3
        except ImportError as exc:
            raise CloudStorageError(
                "boto3 is required for S3-compatible cloud storage"
            ) from exc

        self.bucket = bucket
        self.endpoint_url = endpoint_url

        self.client = boto3.client(
            "s3",
            region_name=region,
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def upload_file(self, local_path: Path, object_key: str) -> str:
        try:
            self.client.upload_file(
                str(local_path),
                self.bucket,
                object_key,
            )
        except Exception as exc:
            raise CloudStorageError(
                f"Cloud upload failed: {exc}"
            ) from exc

        return self.get_url(object_key)

    def exists(self, object_key: str) -> bool:
        try:
            self.client.head_object(
                Bucket=self.bucket,
                Key=object_key,
            )
            return True
        except Exception:
            return False

    def get_url(self, object_key: str) -> str:
        if self.endpoint_url:
            return f"{self.endpoint_url.rstrip('/')}/{self.bucket}/{object_key}"
        return f"s3://{self.bucket}/{object_key}"
