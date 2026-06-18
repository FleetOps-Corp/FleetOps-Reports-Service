"""Criticality policy.

SAD Traceability: implements vehicle criticality classification described in
SAD section 10.3.
"""

from __future__ import annotations

from fleetops_reports.domain.exceptions import InvalidMetricError


class CriticalityPolicy:
    def classify(self, incident_count: int, maintenance_count: int) -> str:
        """Classify operational risk from incident and maintenance recurrence."""
        if incident_count < 0 or maintenance_count < 0:
            raise InvalidMetricError(
                "criticality",
                "incident and maintenance counts must be non-negative",
                {"incident_count": incident_count, "maintenance_count": maintenance_count},
            )
        score = incident_count * 2 + maintenance_count
        if score >= 8:
            return "critical"
        if score >= 4:
            return "warning"
        return "normal"

