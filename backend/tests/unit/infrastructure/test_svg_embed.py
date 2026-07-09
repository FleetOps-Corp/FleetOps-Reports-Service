"""SVG embed helper tests."""

from fleetops_reports.infrastructure.pdf.svg_embed import svg_to_data_uri


def test_svg_to_data_uri_returns_base64_data_uri() -> None:
    svg = b'<svg xmlns="http://www.w3.org/2000/svg"><rect width="10" height="10"/></svg>'
    uri = svg_to_data_uri(svg)
    assert uri.startswith("data:image/svg+xml;base64,")
    assert len(uri) > len("data:image/svg+xml;base64,")
