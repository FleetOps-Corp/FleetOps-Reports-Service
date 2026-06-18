"""Jinja2 template renderer.

SAD Traceability: renders Template View HTML for WeasyPrint PDF generation in
SAD section 10.6. It resolves templates through TEMPLATES_DIR or package data.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from fleetops_reports.config.settings import Settings


class JinjaRenderer:
    def __init__(self, settings: Settings) -> None:
        if settings.templates_dir:
            loader = FileSystemLoader(settings.templates_dir)
        else:
            template_root = resources.files(
                "fleetops_reports.infrastructure.templates"
            ).joinpath("html")
            loader = FileSystemLoader(str(Path(str(template_root))))
        self._environment = Environment(
            loader=loader,
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render(self, template_name: str, context: dict[str, object]) -> str:
        template = self._environment.get_template(template_name)
        return template.render(**context)

