"""Graph logical service.

SAD Traceability: represents Builder Pattern responsibilities for statistical
visualizations in SAD section 10.5. Charts are rendered as deterministic SVG
payloads using stdlib string composition, without a graphics engine dependency.
"""

from __future__ import annotations

from fleetops_reports.application.ports.operational_clients import (
    IncidentRecord,
    MaintenanceRecord,
)
from fleetops_reports.application.services.charts import (
    AvailabilityChartBuilder,
    CriticalRankingChartBuilder,
    EmptyStateChartBuilder,
    IncidentChartBuilder,
    MaintenanceChartBuilder,
    MTTRChartBuilder,
)
from fleetops_reports.domain.models.kpi import KPI
from fleetops_reports.domain.models.vehicle import Vehicle


class GraphService:
    def build_kpi_graph(self, kpis: list[KPI]) -> bytes:
        labels = ", ".join(kpi.name for kpi in kpis)
        svg = (
            "<svg xmlns='http://www.w3.org/2000/svg' width='800' height='240'>"
            "<rect width='800' height='240' fill='#f7fafc'/>"
            "<text x='32' y='120' font-family='Arial' font-size='22'>"
            f"FleetOps KPIs: {labels}"
            "</text></svg>"
        )
        return svg.encode("utf-8")

    def build_availability_chart(self, vehicles: list[Vehicle]) -> bytes:
        """Render availability percentage by operation city.

        SAD Traceability: availability analysis from SAD section 10.1 rendered as
        a bar chart in SAD section 10.5.
        """
        svg = AvailabilityChartBuilder(vehicles).with_title(
            "Availability by Operation City"
        ).build()
        return svg.encode("utf-8")

    def build_incident_chart(self, incidents: list[IncidentRecord]) -> bytes:
        """Render incident distribution by severity and incident type.

        SAD Traceability: incident analytics from SAD section 10.3 rendered as
        a grouped bar chart in SAD section 10.5.
        """
        svg = IncidentChartBuilder(incidents).with_title(
            "Incident Distribution by Severity and Type"
        ).build()
        return svg.encode("utf-8")

    def build_maintenance_chart(self, maintenance: list[MaintenanceRecord]) -> bytes:
        """Render preventive vs corrective maintenance counts.

        SAD Traceability: maintenance indicators from SAD section 10.2 rendered
        as a bar chart in SAD section 10.5.
        """
        svg = MaintenanceChartBuilder(maintenance).with_title(
            "Preventive vs Corrective Maintenance"
        ).build()
        return svg.encode("utf-8")

    def build_mttr_chart(self, mttr_kpi: KPI) -> bytes:
        """Render the current MTTR value as a single-bar chart.

        SAD Traceability: MTTR metric from SAD section 10.2 rendered in SAD
        section 10.5.

        A temporal MTTR evolution chart would require persisted historical KPI
        snapshots or querying AnalyticsRepository; that is out of scope unless
        explicitly added to the report generation flow.
        """
        svg = MTTRChartBuilder(mttr_kpi).with_title("Mean Time To Repair (MTTR)").build()
        return svg.encode("utf-8")

    def build_critical_ranking_chart(
        self,
        incidents: list[IncidentRecord],
        maintenance: list[MaintenanceRecord],
        vehicles: list[Vehicle],
    ) -> bytes:
        """Render a horizontal ranking of vehicles by criticality score.

        SAD Traceability: criticality classification from SAD section 10.3
        rendered as a horizontal bar chart in SAD section 10.5.
        """
        svg = CriticalRankingChartBuilder(
            incidents,
            maintenance,
            vehicles,
        ).with_title("Vehicle Criticality Ranking").build()
        return svg.encode("utf-8")

    def build_empty_state_chart(self, reason: str) -> bytes:
        """Render a neutral placeholder when chart data is unavailable.

        SAD Traceability: preserves report layout for empty datasets in SAD
        section 10.5 without altering chart builder input validation contracts.
        """
        svg = EmptyStateChartBuilder().with_reason(reason).build()
        return svg.encode("utf-8")
