#!/usr/bin/env python3
"""Generate a fixture-backed executive report PDF into docs/reports/."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import UTC, date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
SRC = BACKEND / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fleetops_reports.application.ports.operational_clients import (  # noqa: E402
    AssignmentRecord,
    IncidentRecord,
    MaintenanceRecord,
)
from fleetops_reports.application.services.availability_service import (  # noqa: E402
    AvailabilityService,
)
from fleetops_reports.application.services.incident_service import IncidentService  # noqa: E402
from fleetops_reports.application.services.maintenance_service import (  # noqa: E402
    MaintenanceService,
)
from fleetops_reports.application.services.report_service import ReportService  # noqa: E402
from fleetops_reports.application.use_cases.generate_report import (  # noqa: E402
    GenerateReportCommand,
    GenerateReportUseCase,
)
from fleetops_reports.domain.models.vehicle import Vehicle  # noqa: E402
from fleetops_reports.domain.value_objects.report_period import ReportPeriod  # noqa: E402
from fleetops_reports.infrastructure.pdf.weasyprint_renderer import (  # noqa: E402
    WeasyPrintRenderer,
)
from fleetops_reports.config.settings import Settings  # noqa: E402
from fleetops_reports.infrastructure.templates.jinja_renderer import JinjaRenderer  # noqa: E402
from tests.conftest import (  # noqa: E402
    FakeAssignmentsClient,
    FakeIncidentsClient,
    FakeMaintenanceClient,
    FakeRepository,
    FakeStorage,
    FakeVehiclesClient,
)


def _configure_env() -> None:
    defaults = {
        "APP_ENVIRONMENT": "test",
        "LOG_LEVEL": "INFO",
        "MONGODB_URI": "mongodb://example.invalid:27017",
        "MONGODB_DATABASE": "fleetops_reports_test",
        "MINIO_ENDPOINT": "example.invalid:9000",
        "MINIO_ACCESS_KEY": "placeholder-access-key",
        "MINIO_SECRET_KEY": "placeholder-secret-key",
        "MINIO_SECURE": "false",
        "MINIO_REPORTS_BUCKET": "reports",
        "MINIO_GRAPHS_BUCKET": "graphs",
        "OPERATIONAL_GATEWAY_BASE_URL": "http://example.invalid:8000",
        "CIRCUIT_BREAKER_FAILURE_THRESHOLD": "3",
        "CIRCUIT_BREAKER_RECOVERY_SECONDS": "30",
    }
    for key, value in defaults.items():
        os.environ.setdefault(key, value)


def _load_json(name: str) -> list[dict[str, object]]:
    path = ROOT / "docs" / "simulate" / "fixtures" / name
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_dt(value: str) -> datetime:
    if value.endswith("Z"):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def _load_vehicles() -> list[Vehicle]:
    return [
        Vehicle(
            id_vehiculo=str(item["id_vehiculo"]),
            numero_placa=str(item["numero_placa"]),
            estado_vehiculo=str(item["estado_vehiculo"]),
            ciudad_operacion=str(item["ciudad_operacion"]),
            marca=str(item.get("marca", "FleetOps")),
            modelo=str(item.get("modelo", "Unit")),
            sede_operacion=str(item.get("sede_operacion", "")),
        )
        for item in _load_json("vehiculos.json")
    ]


def _load_assignments() -> list[AssignmentRecord]:
    records: list[AssignmentRecord] = []
    for item in _load_json("asignaciones.json"):
        records.append(
            AssignmentRecord(
                assignment_id=str(item["id"]),
                vehicle_id=str(item["vehiculo_id"]) if item.get("vehiculo_id") else None,
                conductor_id=str(item["conductor_id"]),
                tipo_vehiculo=str(item.get("tipo_vehiculo", "CAMION")),
                start_date=_parse_dt(str(item["fecha_inicio"])),
                end_date=(
                    _parse_dt(str(item["fecha_fin"]))
                    if item.get("fecha_fin")
                    else None
                ),
            )
        )
    return records


def _load_incidents() -> list[IncidentRecord]:
    records: list[IncidentRecord] = []
    for item in _load_json("incidentes.json"):
        records.append(
            IncidentRecord(
                incident_id=str(item["id"]),
                id_conductor=str(item["id_conductor"]),
                placa_vehiculo=str(item["placa_vehiculo"]),
                tipo_incidente=str(item["tipo_incidente"]),
                severity=str(item["gravedad"]),
                occurred_at=_parse_dt(str(item["fecha_hora"])),
            )
        )
    return records


def _load_maintenance() -> list[MaintenanceRecord]:
    records: list[MaintenanceRecord] = []
    for item in _load_json("mantenimiento.json"):
        tipo = item.get("tipo_mantenimiento", 0)
        maintenance_type = (
            str(tipo).upper()
            if isinstance(tipo, str)
            else ("CORRECTIVO" if int(tipo) == 0 else "PREVENTIVO")
        )
        records.append(
            MaintenanceRecord(
                vehicle_id=str(item["id_vehiculo"]),
                maintenance_type=maintenance_type,
                started_at=_parse_dt(str(item["fecha_inicio_mantenimiento"])),
                finished_at=(
                    _parse_dt(str(item["fecha_fin_mantenimiento"]))
                    if item.get("fecha_fin_mantenimiento")
                    else None
                ),
            )
        )
    return records


async def _generate(report_id: str, output_dir: Path) -> Path:
    vehicles = _load_vehicles()
    assignments = _load_assignments()
    incidents = _load_incidents()
    maintenance = _load_maintenance()

    repository = FakeRepository()
    storage = FakeStorage()
    renderer = WeasyPrintRenderer(JinjaRenderer(Settings()))
    report_service = ReportService(repository, storage, renderer)

    use_case = GenerateReportUseCase(
        FakeVehiclesClient(vehicles),
        FakeAssignmentsClient(assignments),
        FakeIncidentsClient(incidents),
        FakeMaintenanceClient(maintenance),
        AvailabilityService(),
        IncidentService(),
        MaintenanceService(),
        report_service,
    )

    report = await use_case.execute(
        GenerateReportCommand(
            report_id=report_id,
            title="FleetOps Executive Report — Fixture Simulation",
            period=ReportPeriod(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31)),
            sede_operacion="Patio Norte Bogotá",
        )
    )

    pdf_bytes = storage._objects[f"{report_id}.pdf"]
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"{report_id}.pdf"
    pdf_path.write_bytes(pdf_bytes)

    metadata_path = output_dir / f"{report_id}.json"
    metadata_path.write_text(
        json.dumps(
            {
                "report_id": report.report_id,
                "title": report.title,
                "status": report.status,
                "document_url": report.document_url,
                "sede_operacion": report.sede_operacion,
                "kpis": [
                    {
                        "name": kpi.name,
                        "metric": {
                            "name": kpi.metric.name,
                            "value": kpi.metric.value,
                            "unit": kpi.metric.unit,
                        },
                        "source": kpi.source,
                    }
                    for kpi in report.kpis
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return pdf_path


def main() -> int:
    _configure_env()
    report_id = f"rep-mock-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"
    output_dir = ROOT / "docs" / "reports"
    pdf_path = asyncio.run(_generate(report_id, output_dir))
    print(f"Generated {pdf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
