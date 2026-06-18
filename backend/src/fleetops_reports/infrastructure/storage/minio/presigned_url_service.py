"""MinIO presigned URL service.

SAD Traceability: implements temporary signed graph URLs required by SAD
deployment flow step 8 so WeasyPrint can fetch graphics safely.
"""

from __future__ import annotations

from datetime import timedelta

from minio import Minio


class PresignedUrlService:
    def __init__(self, client: Minio, bucket: str) -> None:
        self._client = client
        self._bucket = bucket

    def create(self, object_name: str, expires_seconds: int) -> str:
        return self._client.presigned_get_object(
            self._bucket,
            object_name,
            expires=timedelta(seconds=expires_seconds),
        )

