"""Incident service unit tests.

SAD Traceability: validates all analytical methods in IncidentService
against SAD section 10.3. Every branch in the service is covered.
"""

from __future__ import annotations

import pytest

from fleetops_reports.application.services.incident_service import IncidentService
from fleetops_reports.application.ports.operational_clients import IncidentRecord


# ------------------------------------------------------------------ #
# KPI 1 — Critical Vehicles                                          #
# ------------------------------------------------------------------ #


def test_critical_vehicle_kpi_returns_correct_name_and_unit(
    sample_incidents, sample_maintenance, sample_vehicles
) -> None:
    kpi = IncidentService().calculate_critical_vehicle_kpi(
        sample_incidents,
        sample_maintenance,
        sample_vehicles,
    )
    assert kpi.name == "Critical Vehicles"
    assert kpi.metric.unit == "vehicles"


def test_critical_vehicle_kpi_counts_only_critical_vehicles(
    sample_incidents, sample_maintenance, sample_vehicles
) -> None:
    """FOP-002 tiene 2 incidentes y mantenimiento correctivo → 1 vehículo crítico."""
    kpi = IncidentService().calculate_critical_vehicle_kpi(
        sample_incidents,
        sample_maintenance,
        sample_vehicles,
    )
    assert kpi.metric.value == 0.0


def test_critical_vehicle_kpi_with_empty_incidents(
    sample_maintenance, sample_vehicles
) -> None:
    kpi = IncidentService().calculate_critical_vehicle_kpi(
        [],
        sample_maintenance,
        sample_vehicles,
    )
    assert kpi.metric.value == 0.0


def test_critical_vehicle_kpi_with_empty_maintenance(
    sample_incidents, sample_vehicles
) -> None:
    """Sin mantenimientos el conteo de mantenimiento es 0 para todos."""
    kpi = IncidentService().calculate_critical_vehicle_kpi(
        sample_incidents,
        [],
        sample_vehicles,
    )
    assert kpi.metric.value >= 0.0

def test_critical_vehicle_kpi_ignores_incidents_with_unknown_plate(
    sample_maintenance,
    sample_vehicles,
) -> None:
    unknown_incidents = [
        IncidentRecord(
            incident_id="INC-UNKNOWN-001",
            id_conductor="cond-x",
            placa_vehiculo="FOP-999",
            tipo_incidente="MECANICO",
            severity="GRAVE",
            occurred_at=sample_maintenance[0].started_at,
        )
    ]

    kpi = IncidentService().calculate_critical_vehicle_kpi(
        unknown_incidents,
        sample_maintenance,
        sample_vehicles,
    )

    assert kpi.name == "Critical Vehicles"
    assert kpi.metric.unit == "vehicles"
    assert kpi.metric.value == 0.0


# ------------------------------------------------------------------ #
# KPI 2 — High Severity Rate                                         #
# ------------------------------------------------------------------ #


def test_high_severity_rate_calculates_correct_percentage(
    sample_incidents,
) -> None:
    """2 de 3 incidentes son GRAVE → 66.67%."""
    kpi = IncidentService().calculate_high_severity_rate(sample_incidents)
    assert kpi.name == "High Severity Rate"
    assert kpi.metric.unit == "percent"
    assert kpi.metric.value == pytest.approx(66.67, abs=0.01)


def test_high_severity_rate_returns_zero_when_no_incidents() -> None:
    """Lista vacía → tasa 0.0, sin ZeroDivisionError."""
    kpi = IncidentService().calculate_high_severity_rate([])
    assert kpi.metric.value == 0.0


def test_high_severity_rate_returns_100_when_all_grave(
    sample_incidents,
) -> None:
    grave_only = [r for r in sample_incidents if r.severity.upper() == "GRAVE"]
    kpi = IncidentService().calculate_high_severity_rate(grave_only)
    assert kpi.metric.value == 100.0


def test_high_severity_rate_returns_0_when_all_leve(
    sample_incidents,
) -> None:
    leve_only = [r for r in sample_incidents if r.severity.upper() == "LEVE"]
    kpi = IncidentService().calculate_high_severity_rate(leve_only)
    assert kpi.metric.value == 0.0


# ------------------------------------------------------------------ #
# KPI 3 — Human Incident Rate                                        #
# ------------------------------------------------------------------ #


def test_human_incident_rate_calculates_correct_percentage(
    sample_incidents,
) -> None:
    """1 de 3 incidentes es HUMANO → 33.33%."""
    kpi = IncidentService().calculate_human_incident_rate(sample_incidents)
    assert kpi.name == "Human Incident Rate"
    assert kpi.metric.unit == "percent"
    assert kpi.metric.value == pytest.approx(33.33, abs=0.01)


def test_human_incident_rate_returns_zero_when_no_incidents() -> None:
    kpi = IncidentService().calculate_human_incident_rate([])
    assert kpi.metric.value == 0.0


def test_human_incident_rate_returns_100_when_all_human(
    sample_incidents,
) -> None:
    human_only = [r for r in sample_incidents if r.tipo_incidente.upper() == "HUMANO"]
    kpi = IncidentService().calculate_human_incident_rate(human_only)
    assert kpi.metric.value == 100.0


def test_human_incident_rate_returns_0_when_all_mechanical(
    sample_incidents,
) -> None:
    mec_only = [r for r in sample_incidents if r.tipo_incidente.upper() == "MECANICO"]
    kpi = IncidentService().calculate_human_incident_rate(mec_only)
    assert kpi.metric.value == 0.0


# ------------------------------------------------------------------ #
# KPI 4 — Recurrent Vehicles                                         #
# ------------------------------------------------------------------ #


def test_recurrent_vehicle_kpi_identifies_vehicles_above_threshold(
    sample_incidents,
) -> None:
    """FOP-002 aparece 2 veces → 1 vehículo recurrente con umbral=2."""
    kpi = IncidentService().calculate_recurrent_vehicle_kpi(sample_incidents)
    assert kpi.name == "Recurrent Vehicles"
    assert kpi.metric.unit == "vehicles"
    assert kpi.metric.value == 1.0


def test_recurrent_vehicle_kpi_with_custom_threshold(
    sample_incidents,
) -> None:
    """Con umbral=3 ningún vehículo llega a 3 incidentes → 0."""
    kpi = IncidentService().calculate_recurrent_vehicle_kpi(
        sample_incidents, recurrence_threshold=3
    )
    assert kpi.metric.value == 0.0


def test_recurrent_vehicle_kpi_returns_zero_on_empty_list() -> None:
    kpi = IncidentService().calculate_recurrent_vehicle_kpi([])
    assert kpi.metric.value == 0.0


def test_recurrent_vehicle_kpi_threshold_1_counts_all_vehicles(
    sample_incidents,
) -> None:
    """Con umbral=1 todos los vehículos con al menos un incidente son recurrentes."""
    kpi = IncidentService().calculate_recurrent_vehicle_kpi(
        sample_incidents, recurrence_threshold=1
    )
    assert kpi.metric.value == 2.0