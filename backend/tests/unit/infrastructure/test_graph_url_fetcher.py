"""Tests for WeasyPrint graph URL fetcher."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from fleetops_reports.infrastructure.pdf.graph_url_fetcher import fetch_graph_url
from fleetops_reports.infrastructure.pdf.svg_embed import svg_to_data_uri


def test_fetch_graph_url_supports_data_uri() -> None:
    svg = b"<svg xmlns='http://www.w3.org/2000/svg'></svg>"
    payload = fetch_graph_url(svg_to_data_uri(svg))
    assert payload["string"] == svg
    assert payload["mime_type"].startswith("image/svg+xml")


def test_fetch_graph_url_fetches_http_resource() -> None:
    svg = b"<svg xmlns='http://www.w3.org/2000/svg'><rect/></svg>"
    response = MagicMock()
    response.content = svg
    response.headers = {"content-type": "image/svg+xml"}
    response.url = "https://minio.test/rep-001-availability.svg?expires=600"
    response.raise_for_status = MagicMock()

    with patch(
        "fleetops_reports.infrastructure.pdf.graph_url_fetcher.httpx.get",
        return_value=response,
    ) as mocked_get:
        payload = fetch_graph_url(
            "https://minio.test/rep-001-availability.svg?expires=600",
        )

    mocked_get.assert_called_once()
    assert payload["string"] == svg
    assert payload["mime_type"] == "image/svg+xml"


def test_fetch_graph_url_raises_on_http_error() -> None:
    response = MagicMock()
    response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "not found",
        request=MagicMock(),
        response=MagicMock(status_code=404),
    )

    with (
        patch(
            "fleetops_reports.infrastructure.pdf.graph_url_fetcher.httpx.get",
            return_value=response,
        ),
        pytest.raises(httpx.HTTPStatusError),
    ):
        fetch_graph_url("https://minio.test/missing.svg")
