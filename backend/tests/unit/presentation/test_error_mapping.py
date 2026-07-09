"""HTTP status mapping for domain errors."""

import pytest

from fleetops_reports.domain.exceptions import (
    OperationalGatewayAuthError,
    ReportGenerationError,
)
from fleetops_reports.presentation.api.error_mapping import http_status_for_domain_error


def test_operational_gateway_auth_error_maps_to_503() -> None:
    error = OperationalGatewayAuthError("login rejected")
    assert http_status_for_domain_error(error) == 503


def test_report_generation_upstream_auth_maps_to_503() -> None:
    error = ReportGenerationError(
        "rep-001",
        "Client error '401 Unauthorized' for url 'http://gateway/auth/login'",
    )
    assert http_status_for_domain_error(error) == 503


def test_report_generation_other_upstream_maps_to_502() -> None:
    error = ReportGenerationError("rep-001", "Connection timeout")
    assert http_status_for_domain_error(error) == 502


@pytest.mark.parametrize(
    "reason",
    ["invalid metric", "empty dataset"],
)
def test_other_domain_errors_default_to_422(reason: str) -> None:
    from fleetops_reports.domain.exceptions import InvalidMetricError

    error = InvalidMetricError("kpi", reason)
    assert http_status_for_domain_error(error) == 422
