"""Graph logical service.

SAD Traceability: represents Builder Pattern responsibilities for statistical
visualizations in SAD section 10.5. The archetype returns a deterministic SVG
payload so the flow runs locally without a graphics engine dependency.
"""

from __future__ import annotations

from fleetops_reports.domain.models.kpi import KPI


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

