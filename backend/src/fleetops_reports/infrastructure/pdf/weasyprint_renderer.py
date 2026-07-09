"""WeasyPrint PDF renderer.

SAD Traceability: concrete PDF generation pipeline for SAD section 10.6.
"""

from __future__ import annotations

import asyncio

from weasyprint import HTML

from fleetops_reports.infrastructure.pdf.graph_url_fetcher import fetch_graph_url
from fleetops_reports.infrastructure.templates.jinja_renderer import JinjaRenderer


class WeasyPrintRenderer:
    def __init__(self, jinja_renderer: JinjaRenderer) -> None:
        self._jinja_renderer = jinja_renderer

    async def render(self, template_name: str, context: dict[str, object]) -> bytes:
        html = self._jinja_renderer.render(template_name, context)
        return await asyncio.to_thread(
            lambda: HTML(string=html, url_fetcher=fetch_graph_url).write_pdf()
        )
