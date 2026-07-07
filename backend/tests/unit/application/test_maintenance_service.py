"""Maintenance service tests.

SAD Traceability: validates logical service for SAD process 10.2.
hcarabali add validates all analytical methods in MaintenanceService
against SAD section 10.2. Every branch and business rule is covered.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from fleetops_reports.application.ports.operational_clients import MaintenanceRecord
from fleetops_reports.application.services.maintenance_service import MaintenanceService

# ------------------------------------------------------------------ #
# KPI 0 — MTTR (completar cobertura del método existente)            #
# ------------------------------------------------------------------ #


def test_maintenance_service_calculates_mttr(sample_maintenance) -> None:
    kpi = MaintenanceService().calculate_mttr_kpi(sample_maintenance)
    assert kpi.name == "Mean Time To Repair"
    assert kpi.metric.unit == "hours"


def test_maintenance_service_mttr_value_is_average_of_closed_intervals(
    sample_maintenance,
) -> None:
    """(5h + 2h) / 2 = 3.5h."""
    kpi = MaintenanceService().calculate_mttr_kpi(sample_maintenance)
    assert kpi.metric.value == pytest.approx(3.5, abs=0.01)


def test_maintenance_service_mttr_ignores_open_records() -> None:
    """Registros con finished_at=None son filtrados; solo el cerrado se calcula."""
    now = datetime.now(UTC)
    records = [
        MaintenanceRecord("veh-001", "CORRECTIVO", now - timedelta(hours=4), now),
        MaintenanceRecord("veh-002", "PREVENTIVO", now - timedelta(hours=2), None),
    ]
    kpi = MaintenanceService().calculate_mttr_kpi(records)
    assert kpi.metric.value == pytest.approx(4.0, abs=0.01)


def test_maintenance_service_mttr_returns_zero_when_all_records_are_open() -> None:
    now = datetime.now(UTC)
    records = [
        MaintenanceRecord("veh-001", "CORRECTIVO", now - timedelta(hours=3), None),
    ]
    kpi = MaintenanceService().calculate_mttr_kpi(records)
    assert kpi.metric.value == 0.0


def test_maintenance_service_mttr_returns_zero_on_empty_list() -> None:
    kpi = MaintenanceService().calculate_mttr_kpi([])
    assert kpi.metric.value == 0.0


# ------------------------------------------------------------------ #
# KPI 1 — Preventive Maintenance Count                               #
# ------------------------------------------------------------------ #


def test_preventive_count_kpi_returns_correct_name_and_unit(
    sample_maintenance,
) -> None:
    kpi = MaintenanceService().calculate_preventive_count_kpi(sample_maintenance)
    assert kpi.name == "Preventive Maintenance Count"
    assert kpi.metric.name == "preventive_maintenance_count"
    assert kpi.metric.unit == "maintenances"
    assert kpi.source == "maintenance"


def test_preventive_count_kpi_counts_only_preventivo(sample_maintenance) -> None:
    """Sample tiene 1 PREVENTIVO (veh-003)."""
    kpi = MaintenanceService().calculate_preventive_count_kpi(sample_maintenance)
    assert kpi.metric.value == 1.0


def test_preventive_count_kpi_returns_zero_when_all_corrective() -> None:
    now = datetime.now(UTC)
    records = [
        MaintenanceRecord("veh-001", "CORRECTIVO", now - timedelta(hours=1), now),
        MaintenanceRecord("veh-002", "CORRECTIVO", now - timedelta(hours=2), now),
    ]
    kpi = MaintenanceService().calculate_preventive_count_kpi(records)
    assert kpi.metric.value == 0.0


def test_preventive_count_kpi_counts_all_when_all_preventive() -> None:
    now = datetime.now(UTC)
    records = [
        MaintenanceRecord("veh-001", "PREVENTIVO", now - timedelta(hours=1), now),
        MaintenanceRecord("veh-002", "PREVENTIVO", now - timedelta(hours=2), now),
        MaintenanceRecord("veh-003", "PREVENTIVO", now - timedelta(hours=3), now),
    ]
    kpi = MaintenanceService().calculate_preventive_count_kpi(records)
    assert kpi.metric.value == 3.0


def test_preventive_count_kpi_returns_zero_on_empty_list() -> None:
    kpi = MaintenanceService().calculate_preventive_count_kpi([])
    assert kpi.metric.value == 0.0


# ------------------------------------------------------------------ #
# KPI 2 — Corrective Maintenance Count                               #
# ------------------------------------------------------------------ #


def test_corrective_count_kpi_returns_correct_name_and_unit(
    sample_maintenance,
) -> None:
    kpi = MaintenanceService().calculate_corrective_count_kpi(sample_maintenance)
    assert kpi.name == "Corrective Maintenance Count"
    assert kpi.metric.name == "corrective_maintenance_count"
    assert kpi.metric.unit == "maintenances"
    assert kpi.source == "maintenance"


def test_corrective_count_kpi_counts_only_correctivo(sample_maintenance) -> None:
    """Sample tiene 1 CORRECTIVO (veh-002)."""
    kpi = MaintenanceService().calculate_corrective_count_kpi(sample_maintenance)
    assert kpi.metric.value == 1.0


def test_corrective_count_kpi_returns_zero_when_all_preventive() -> None:
    now = datetime.now(UTC)
    records = [
        MaintenanceRecord("veh-001", "PREVENTIVO", now - timedelta(hours=1), now),
        MaintenanceRecord("veh-002", "PREVENTIVO", now - timedelta(hours=2), now),
    ]
    kpi = MaintenanceService().calculate_corrective_count_kpi(records)
    assert kpi.metric.value == 0.0


def test_corrective_count_kpi_counts_all_when_all_corrective() -> None:
    now = datetime.now(UTC)
    records = [
        MaintenanceRecord("veh-001", "CORRECTIVO", now - timedelta(hours=1), now),
        MaintenanceRecord("veh-002", "CORRECTIVO", now - timedelta(hours=2), now),
    ]
    kpi = MaintenanceService().calculate_corrective_count_kpi(records)
    assert kpi.metric.value == 2.0


def test_corrective_count_kpi_returns_zero_on_empty_list() -> None:
    kpi = MaintenanceService().calculate_corrective_count_kpi([])
    assert kpi.metric.value == 0.0


# ------------------------------------------------------------------ #
# KPI 3 — Preventive to Corrective Ratio                             #
# ------------------------------------------------------------------ #


def test_preventive_ratio_kpi_returns_correct_name_and_unit(
    sample_maintenance,
) -> None:
    kpi = MaintenanceService().calculate_preventive_ratio_kpi(sample_maintenance)
    assert kpi.name == "Preventive to Corrective Ratio"
    assert kpi.metric.name == "preventive_corrective_ratio"
    assert kpi.metric.unit == "ratio"
    assert kpi.source == "maintenance"


def test_preventive_ratio_kpi_one_to_one(sample_maintenance) -> None:
    """1 PREVENTIVO + 1 CORRECTIVO → ratio 1.0."""
    kpi = MaintenanceService().calculate_preventive_ratio_kpi(sample_maintenance)
    assert kpi.metric.value == pytest.approx(1.0, abs=0.01)


def test_preventive_ratio_kpi_two_to_one() -> None:
    """2 PREVENTIVO + 1 CORRECTIVO → ratio 2.0."""
    now = datetime.now(UTC)
    records = [
        MaintenanceRecord("veh-001", "PREVENTIVO", now - timedelta(hours=1), now),
        MaintenanceRecord("veh-002", "PREVENTIVO", now - timedelta(hours=2), now),
        MaintenanceRecord("veh-003", "CORRECTIVO", now - timedelta(hours=3), now),
    ]
    kpi = MaintenanceService().calculate_preventive_ratio_kpi(records)
    assert kpi.metric.value == pytest.approx(2.0, abs=0.01)


def test_preventive_ratio_kpi_returns_zero_when_no_correctives() -> None:
    """Sin correctivos no hay división por cero — retorna 0.0."""
    now = datetime.now(UTC)
    records = [
        MaintenanceRecord("veh-001", "PREVENTIVO", now - timedelta(hours=1), now),
        MaintenanceRecord("veh-002", "PREVENTIVO", now - timedelta(hours=2), now),
    ]
    kpi = MaintenanceService().calculate_preventive_ratio_kpi(records)
    assert kpi.metric.value == 0.0


def test_preventive_ratio_kpi_returns_zero_on_empty_list() -> None:
    kpi = MaintenanceService().calculate_preventive_ratio_kpi([])
    assert kpi.metric.value == 0.0


def test_preventive_ratio_kpi_returns_zero_when_no_preventives() -> None:
    """0 preventivos / N correctivos = 0.0."""
    now = datetime.now(UTC)
    records = [
        MaintenanceRecord("veh-001", "CORRECTIVO", now - timedelta(hours=1), now),
        MaintenanceRecord("veh-002", "CORRECTIVO", now - timedelta(hours=2), now),
    ]
    kpi = MaintenanceService().calculate_preventive_ratio_kpi(records)
    assert kpi.metric.value == 0.0


# ------------------------------------------------------------------ #
# KPI 4 — High Recurrence Vehicles                                   #
# ------------------------------------------------------------------ #


def test_high_recurrence_kpi_returns_correct_name_and_unit(
    sample_maintenance,
) -> None:
    kpi = MaintenanceService().calculate_high_recurrence_vehicle_kpi(sample_maintenance)
    assert kpi.name == "High Recurrence Vehicles"
    assert kpi.metric.name == "high_recurrence_vehicle_count"
    assert kpi.metric.unit == "vehicles"
    assert kpi.source == "maintenance"


def test_high_recurrence_kpi_default_threshold_no_recurrent(
    sample_maintenance,
) -> None:
    """Sample: veh-002 ×1, veh-003 ×1 — ninguno supera threshold=2."""
    kpi = MaintenanceService().calculate_high_recurrence_vehicle_kpi(sample_maintenance)
    assert kpi.metric.value == 0.0


def test_high_recurrence_kpi_detects_vehicle_at_threshold() -> None:
    """veh-002 aparece 2 veces → 1 vehículo recurrente con threshold=2."""
    now = datetime.now(UTC)
    records = [
        MaintenanceRecord("veh-002", "CORRECTIVO", now - timedelta(hours=5), now),
        MaintenanceRecord("veh-002", "PREVENTIVO", now - timedelta(hours=2), now),
        MaintenanceRecord("veh-003", "PREVENTIVO", now - timedelta(hours=1), now),
    ]
    kpi = MaintenanceService().calculate_high_recurrence_vehicle_kpi(records)
    assert kpi.metric.value == 1.0


def test_high_recurrence_kpi_custom_threshold_1_counts_all_vehicles() -> None:
    """Con threshold=1 todos los vehículos con al menos 1 registro son recurrentes."""
    now = datetime.now(UTC)
    records = [
        MaintenanceRecord("veh-001", "CORRECTIVO", now - timedelta(hours=3), now),
        MaintenanceRecord("veh-002", "PREVENTIVO", now - timedelta(hours=2), now),
        MaintenanceRecord("veh-003", "CORRECTIVO", now - timedelta(hours=1), now),
    ]
    kpi = MaintenanceService().calculate_high_recurrence_vehicle_kpi(
        records, recurrence_threshold=1
    )
    assert kpi.metric.value == 3.0


def test_high_recurrence_kpi_high_threshold_returns_zero() -> None:
    """Con threshold=10 ningún vehículo supera el umbral."""
    now = datetime.now(UTC)
    records = [
        MaintenanceRecord("veh-001", "CORRECTIVO", now - timedelta(hours=1), now),
        MaintenanceRecord("veh-001", "PREVENTIVO", now - timedelta(hours=2), now),
    ]
    kpi = MaintenanceService().calculate_high_recurrence_vehicle_kpi(
        records, recurrence_threshold=10
    )
    assert kpi.metric.value == 0.0


def test_high_recurrence_kpi_returns_zero_on_empty_list() -> None:
    kpi = MaintenanceService().calculate_high_recurrence_vehicle_kpi([])
    assert kpi.metric.value == 0.0
