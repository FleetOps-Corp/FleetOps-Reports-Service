"""Maintenance analytics logical service.

SAD Traceability: calculates MTTR and maintenance indicators from SAD section
10.2 using a domain policy rather than infrastructure logic.
"""

from __future__ import annotations

from fleetops_reports.application.ports.operational_clients import MaintenanceRecord
from fleetops_reports.domain.models.kpi import KPI
from fleetops_reports.domain.policies.mttr_policy import MTTRPolicy


class MaintenanceService:
    def __init__(self, policy: MTTRPolicy | None = None) -> None:
        self._policy = policy or MTTRPolicy()

    def calculate_mttr_kpi(self, records: list[MaintenanceRecord]) -> KPI:
        intervals = [(record.started_at, record.finished_at) for record in records]
        metric = self._policy.calculate_hours(intervals)
        return KPI.create_now(name="Mean Time To Repair", metric=metric, source="maintenance")

