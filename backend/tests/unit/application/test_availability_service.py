"""Availability service tests.

SAD Traceability: validates logical service for SAD process 10.1.
"""

import pytest

from fleetops_reports.application.services.availability_service import AvailabilityService


def test_availability_service_calculates_kpi(sample_vehicles) -> None:
    kpi = AvailabilityService().calculate_global_kpi(sample_vehicles)
    assert kpi.name == "Fleet Availability"
    assert kpi.metric.value == pytest.approx(66.67, abs=0.01)

