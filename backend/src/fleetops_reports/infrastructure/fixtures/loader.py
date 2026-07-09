"""Load bundled JSON fixtures shipped with the Reports service."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from importlib import resources
from typing import Any, cast

from fleetops_reports.application.ports.operational_clients import (
    AssignmentRecord,
    IncidentRecord,
    MaintenanceRecord,
)
from fleetops_reports.domain.models.vehicle import Vehicle


def _load_json(name: str) -> list[dict[str, Any]]:
    package = resources.files("fleetops_reports.infrastructure.fixtures") / "data"
    return cast(list[dict[str, Any]], json.loads((package / name).read_text(encoding="utf-8")))


def _parse_dt(value: str) -> datetime:
    if value.endswith("Z"):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def load_fixture_vehicles() -> list[Vehicle]:
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


def load_fixture_assignments() -> list[AssignmentRecord]:
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


def load_fixture_incidents() -> list[IncidentRecord]:
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


def load_fixture_maintenance() -> list[MaintenanceRecord]:
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
