"""Map domain failures to HTTP status codes for REST routes."""

from __future__ import annotations

from fastapi import status

from fleetops_reports.domain.exceptions import (
    DomainError,
    OperationalGatewayAuthError,
    ReportGenerationError,
)


def http_status_for_domain_error(error: DomainError) -> int:
    if isinstance(error, OperationalGatewayAuthError):
        return status.HTTP_503_SERVICE_UNAVAILABLE
    if isinstance(error, ReportGenerationError):
        reason = str(error.details.get("reason", "")).lower()
        if any(
            marker in reason
            for marker in (
                "401 unauthorized",
                "/auth/login",
                "operational gateway",
                "operational_gateway_auth_failed",
            )
        ):
            return status.HTTP_503_SERVICE_UNAVAILABLE
        return status.HTTP_502_BAD_GATEWAY
    return status.HTTP_422_UNPROCESSABLE_ENTITY
