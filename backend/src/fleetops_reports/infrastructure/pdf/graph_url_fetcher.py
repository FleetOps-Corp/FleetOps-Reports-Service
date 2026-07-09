"""HTTP fetcher for WeasyPrint graph resources.

SAD Traceability: downloads chart SVGs via MinIO presigned URLs during PDF
rendering (SAD deployment flow step 8).
"""

from __future__ import annotations

import base64
from typing import Any
from urllib.parse import unquote_to_bytes

import httpx

_DEFAULT_TIMEOUT_SECONDS = 30.0


def _fetch_data_uri(url: str) -> dict[str, Any]:
    header, payload = url.split(",", 1)
    mime_type = header[5:].split(";", 1)[0] or "application/octet-stream"
    content = (
        base64.b64decode(payload)
        if ";base64" in header
        else unquote_to_bytes(payload)
    )
    return {
        "string": content,
        "mime_type": mime_type,
        "encoding": None,
        "redirected_url": url,
    }


def fetch_graph_url(
    url: str,
    *,
    timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Fetch a graph resource URL for WeasyPrint rendering."""
    if url.startswith("data:"):
        return _fetch_data_uri(url)

    response = httpx.get(
        url,
        timeout=timeout_seconds,
        follow_redirects=True,
        verify=False,
    )
    response.raise_for_status()
    content_type = response.headers.get("content-type", "image/svg+xml")
    return {
        "string": response.content,
        "mime_type": content_type.split(";", 1)[0].strip(),
        "encoding": None,
        "redirected_url": str(response.url),
    }
