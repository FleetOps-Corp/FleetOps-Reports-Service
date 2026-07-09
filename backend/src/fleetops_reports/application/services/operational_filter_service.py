"""Operational data filtering helpers."""

from __future__ import annotations

from datetime import date, datetime, time

from fleetops_reports.application.ports.operational_clients import (
    IncidentRecord,
    MaintenanceRecord,
)
from fleetops_reports.domain.models.vehicle import Vehicle


def _normalize(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().casefold()
    return normalized or None


def filter_vehicles_by_sede(
    vehicles: list[Vehicle],
    sede_operacion: str | None,
) -> list[Vehicle]:
    normalized = _normalize(sede_operacion)
    if not normalized:
        return vehicles
    return [
        vehicle
        for vehicle in vehicles
        if vehicle.sede_operacion.strip().casefold() == normalized
    ]


def filter_vehicles_by_ciudad(
    vehicles: list[Vehicle],
    ciudad_operacion: str | None,
) -> list[Vehicle]:
    normalized = _normalize(ciudad_operacion)
    if not normalized:
        return vehicles
    return [
        vehicle
        for vehicle in vehicles
        if vehicle.ciudad_operacion.strip().casefold() == normalized
    ]


def filter_vehicles_for_report(
    vehicles: list[Vehicle],
    *,
    sede_operacion: str | None = None,
    ciudad_operacion: str | None = None,
) -> list[Vehicle]:
    filtered = filter_vehicles_by_sede(vehicles, sede_operacion)
    return filter_vehicles_by_ciudad(filtered, ciudad_operacion)


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


def _to_utc_datetime(value: date | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.combine(value, time.min)


def filter_incidents_by_period(
    incidents: list[IncidentRecord],
    start_date: date,
    end_date: date,
) -> list[IncidentRecord]:
    period_start = _to_utc_datetime(start_date)
    period_end = _to_utc_datetime(end_date)
    return [
        incident
        for incident in incidents
        if period_start.date() <= incident.occurred_at.date() <= period_end.date()
    ]


def filter_maintenance_by_period(
    maintenance: list[MaintenanceRecord],
    start_date: date,
    end_date: date,
) -> list[MaintenanceRecord]:
    period_start = _to_utc_datetime(start_date)
    period_end = _to_utc_datetime(end_date)
    return [
        record
        for record in maintenance
        if period_start.date() <= record.started_at.date() <= period_end.date()
    ]
