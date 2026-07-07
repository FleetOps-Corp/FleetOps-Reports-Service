"""Template logical service.

SAD Traceability: prepares Template View data for Jinja2 executive reports in
SAD section 10.6.
"""

from __future__ import annotations

from fleetops_reports.domain.models.report import Report


class TemplateService:
    def build_context(self, report: Report, graph_urls: dict[str, str]) -> dict[str, object]:
        return {
            "report_id": report.report_id,
            "title": report.title,
            "period": report.period.label(),
            "status": report.status,
            "sede_operacion": report.sede_operacion or "All sites",
            "created_at": report.created_at.strftime("%Y-%m-%d %H:%M UTC"),
            "graph_urls": graph_urls,
            "kpis": [
                {
                    "name": kpi.name,
                    "metric": kpi.metric.name,
                    "value": kpi.metric.value,
                    "unit": kpi.metric.unit,
                    "source": kpi.source,
                }
                for kpi in report.kpis
            ],
        }
