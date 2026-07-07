"""Template logical service.

SAD Traceability: prepares Template View data for Jinja2 executive reports in
SAD section 10.6.
"""

from __future__ import annotations

from fleetops_reports.domain.models.report import Report
from fleetops_reports.domain.models.vehicle import Vehicle

KPI_DESCRIPTIONS: dict[str, str] = {
    "fleet_availability": "Share of fleet units that are operational and ready for dispatch.",
    "MTTR": "Average elapsed time to close corrective maintenance work orders.",
    "critical_vehicle_count": "Vehicles with grave or critical incidents during the period.",
    "high_severity_rate": "Percentage of incidents classified as high or grave severity.",
    "human_incident_rate": "Percentage of incidents attributed to human-factor causes.",
    "recurrent_vehicle_count": "Vehicles with two or more incidents in the reporting period.",
}

VEHICLE_STATUS_ORDER: dict[str, int] = {
    "DISPONIBLE": 0,
    "EN_RUTA": 1,
    "ASIGNADO": 2,
    "EN_MANTENIMIENTO": 3,
    "FUERA_DE_SERVICIO": 4,
}

VEHICLE_STATUS_LABELS: dict[str, str] = {
    "DISPONIBLE": "Available",
    "EN_MANTENIMIENTO": "In maintenance",
    "FUERA_DE_SERVICIO": "Out of service",
    "EN_RUTA": "On route",
    "ASIGNADO": "Assigned",
}


class TemplateService:
    def build_context(
        self,
        report: Report,
        graph_urls: dict[str, str],
        *,
        vehicles: list[Vehicle] | None = None,
    ) -> dict[str, object]:
        return {
            "report_id": report.report_id,
            "title": report.title,
            "period": report.period.label(),
            "status": report.status,
            "sede_operacion": report.sede_operacion or "All sites",
            "created_at": report.created_at.strftime("%Y-%m-%d %H:%M UTC"),
            "graph_urls": graph_urls,
            "vehicles": self._build_vehicle_rows(vehicles or []),
            "kpis": [
                {
                    "name": kpi.name,
                    "description": KPI_DESCRIPTIONS.get(
                        kpi.metric.name,
                        "Operational indicator for executive monitoring.",
                    ),
                    "value": kpi.metric.value,
                    "unit": kpi.metric.unit,
                    "source": kpi.source,
                }
                for kpi in report.kpis
            ],
        }

    def _build_vehicle_rows(self, vehicles: list[Vehicle]) -> list[dict[str, str]]:
        sorted_vehicles = sorted(
            vehicles,
            key=lambda vehicle: (
                VEHICLE_STATUS_ORDER.get(vehicle.estado_vehiculo, 99),
                vehicle.estado_vehiculo,
                vehicle.marca,
                vehicle.modelo,
                vehicle.numero_placa,
            ),
        )
        return [
            {
                "plate": vehicle.numero_placa,
                "brand_model": f"{vehicle.marca} {vehicle.modelo}".strip(),
                "status": vehicle.estado_vehiculo,
                "status_label": VEHICLE_STATUS_LABELS.get(
                    vehicle.estado_vehiculo,
                    vehicle.estado_vehiculo.replace("_", " ").title(),
                ),
                "sede_operacion": vehicle.sede_operacion or vehicle.ciudad_operacion,
            }
            for vehicle in sorted_vehicles
        ]
