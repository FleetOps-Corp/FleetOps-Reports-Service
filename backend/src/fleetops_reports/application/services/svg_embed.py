"""Helpers for embedding SVG charts in WeasyPrint PDF output."""

from __future__ import annotations

import base64


def svg_to_data_uri(svg_content: bytes) -> str:
    """Return a data URI WeasyPrint can render without fetching external URLs."""
    encoded = base64.b64encode(svg_content).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"
