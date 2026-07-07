"""Report domain model.

SAD Traceability: models executive PDF reports generated with Jinja2,
WeasyPrint and MinIO as specified in section 10.6 and ADR-003.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from fleetops_reports.domain.exceptions import ReportGenerationError
from fleetops_reports.domain.models.kpi import KPI
from fleetops_reports.domain.value_objects.report_period import ReportPeriod


@dataclass
class Report:
    report_id: str
    title: str
    period: ReportPeriod
    kpis: list[KPI]
    status: str = "draft"
    document_url: str | None = None
    sede_operacion: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def mark_generated(self, document_url: str) -> None:
        if not document_url:
            raise ReportGenerationError(self.report_id, "document URL is required")
        self.status = "generated"
        self.document_url = document_url

