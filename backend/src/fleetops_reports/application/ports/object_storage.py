"""Object storage port.

SAD Traceability: MinIO abstraction for graph resources, executive PDFs and
temporary presigned URLs from ADR-003 and SAD section 11.5 step 8.
"""

from __future__ import annotations

from typing import Protocol


class ObjectStorage(Protocol):
    async def upload_report_pdf(self, report_id: str, content: bytes) -> str:
        """Store a generated PDF and return its object URI."""

    async def upload_graph(self, graph_name: str, content: bytes) -> str:
        """Store a generated graph and return its object URI."""

    async def create_presigned_url(self, object_name: str, expires_seconds: int) -> str:
        """Create a temporary signed URL for WeasyPrint-safe graph access."""

    async def download_report_pdf(self, object_name: str) -> bytes:
        """Download a stored PDF report object from MinIO."""

    async def download_graph(self, object_name: str) -> bytes:
        """Download a stored graph SVG object from MinIO."""

