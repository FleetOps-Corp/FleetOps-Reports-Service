"""Operational data filtering helpers."""

from __future__ import annotations

from fleetops_reports.application.ports.operational_clients import (
    IncidentRecord,
    MaintenanceRecord,
)
from fleetops_reports.domain.models.vehicle import Vehicle


def filter_vehicles_by_sede(
    vehicles: list[Vehicle],
    sede_operacion: str | None,
) -> list[Vehicle]:
    if not sede_operacion:
        return vehicles
    normalized = sede_operacion.strip().casefold()
    return [
        vehicle
        for vehicle in vehicles
        if vehicle.sede_operacion.strip().casefold() == normalized
    ]


def filter_incidents_for_vehicles(
    incidents: list[IncidentRecord],
    vehicles: list[Vehicle],
) -> list[IncidentRecord]:
    if not vehicles:
        return []
    plates = {vehicle.numero_placa for vehicle in vehicles if vehicle.numero_placa}
    return [incident for incident in incidents if incident.placa_vehiculo in plates]


def filter_maintenance_for_vehicles(
    maintenance: list[MaintenanceRecord],
    vehicles: list[Vehicle],
) -> list[MaintenanceRecord]:
    if not vehicles:
        return []
    vehicle_ids = {vehicle.id_vehiculo for vehicle in vehicles}
    return [record for record in maintenance if record.vehicle_id in vehicle_ids]
