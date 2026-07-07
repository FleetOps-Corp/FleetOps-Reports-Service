"""Analytics repository port.

SAD Traceability: Repository Pattern abstraction for MongoDB Atlas analytical
persistence from ADR-002.
"""

from __future__ import annotations

from typing import Protocol

from fleetops_reports.domain.models.report import Report


class AnalyticsRepository(Protocol):
    async def save_report(self, report: Report) -> Report:
        """Persist executive report metadata and analytical summary."""

    async def get_report(self, report_id: str) -> Report | None:
        """Retrieve an analytical report by identifier."""

    async def list_reports(self, sede_operacion: str | None = None) -> list[Report]:
        """List stored reports, optionally filtered by operation site."""

