"""MinIO object storage adapter.

SAD Traceability: stores graph resources and PDF reports separately from
MongoDB per ADR-003.
"""

from __future__ import annotations

import asyncio
from io import BytesIO

from minio import Minio

from fleetops_reports.config.settings import Settings
from fleetops_reports.infrastructure.storage.minio.presigned_url_service import PresignedUrlService


class MinioObjectStorage:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self._presigned = PresignedUrlService(self._client, settings.minio_graphs_bucket)

    async def ensure_buckets(self) -> None:
        for bucket in (self._settings.minio_reports_bucket, self._settings.minio_graphs_bucket):
            exists = await asyncio.to_thread(self._client.bucket_exists, bucket)
            if not exists:
                await asyncio.to_thread(self._client.make_bucket, bucket)

    async def upload_report_pdf(self, report_id: str, content: bytes) -> str:
        await self.ensure_buckets()
        object_name = f"{report_id}.pdf"
        await asyncio.to_thread(
            self._client.put_object,
            self._settings.minio_reports_bucket,
            object_name,
            BytesIO(content),
            len(content),
            content_type="application/pdf",
        )
        return object_name

    async def upload_graph(self, graph_name: str, content: bytes) -> str:
        await self.ensure_buckets()
        await asyncio.to_thread(
            self._client.put_object,
            self._settings.minio_graphs_bucket,
            graph_name,
            BytesIO(content),
            len(content),
            content_type="image/svg+xml",
        )
        return graph_name

    async def create_presigned_url(self, object_name: str, expires_seconds: int) -> str:
        return await asyncio.to_thread(
            self._presigned.create,
            object_name,
            expires_seconds,
        )

    async def download_report_pdf(self, object_name: str) -> bytes:
        await self.ensure_buckets()

        def _download() -> bytes:
            response = self._client.get_object(
                self._settings.minio_reports_bucket,
                object_name,
            )
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()

        return await asyncio.to_thread(_download)

