"""Template logical service.

SAD Traceability: prepares Template View data for Jinja2 executive reports in
SAD section 10.6.
"""

from __future__ import annotations

from fleetops_reports.domain.models.report import Report


class TemplateService:
    def build_context(self, report: Report, graph_url: str) -> dict[str, object]:
        return {
            "report_id": report.report_id,
            "title": report.title,
            "period": report.period.label(),
            "status": report.status,
            "graph_url": graph_url,
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

