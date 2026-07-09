"""Tests for SVG data URI helpers."""

from fleetops_reports.application.services.svg_embed import svg_to_data_uri


def test_svg_to_data_uri_returns_base64_data_uri() -> None:
    svg = b"<svg xmlns='http://www.w3.org/2000/svg'></svg>"
    uri = svg_to_data_uri(svg)
    assert uri.startswith("data:image/svg+xml;base64,")
