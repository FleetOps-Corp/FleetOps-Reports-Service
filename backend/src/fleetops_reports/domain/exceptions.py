"""Domain exceptions for FleetOps Reports.

SAD Traceability: supports the rich domain model implied by the analytical
business rules for availability, MTTR, criticality, traceability and executive
report generation in SAD sections 6, 7 and 10.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(eq=False)
class DomainError(Exception):
    """Base exception for business rule violations.

    The exception carries a stable machine-readable code plus optional details
    so application use cases can translate domain failures into API responses
    without coupling domain code to FastAPI or transport concerns.
    """

    message: str
    code: str = "DOMAIN_ERROR"
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class VehicleNotAvailableError(DomainError):
    """Raised when availability policy marks a requested vehicle unavailable."""

    def __init__(self, vehicle_id: str, reason: str) -> None:
        super().__init__(
            message=f"Vehicle '{vehicle_id}' is not available: {reason}",
            code="VEHICLE_NOT_AVAILABLE",
            details={"vehicle_id": vehicle_id, "reason": reason},
        )


class InvalidMetricError(DomainError):
    """Raised when an analytical metric cannot be represented or calculated."""

    def __init__(self, metric_name: str, reason: str, value: Any | None = None) -> None:
        super().__init__(
            message=f"Invalid metric '{metric_name}': {reason}",
            code="INVALID_METRIC",
            details={"metric_name": metric_name, "reason": reason, "value": value},
        )


class ReportGenerationError(DomainError):
    """Raised when a report violates domain-level generation rules."""

    def __init__(self, report_id: str, reason: str) -> None:
        super().__init__(
            message=f"Report '{report_id}' cannot be generated: {reason}",
            code="REPORT_GENERATION_ERROR",
            details={"report_id": report_id, "reason": reason},
        )


class ReportNotFoundError(DomainError):
    """Raised when a requested report does not exist or has no stored artifact."""

    def __init__(self, report_id: str) -> None:
        super().__init__(
            message=f"Report '{report_id}' was not found",
            code="REPORT_NOT_FOUND",
            details={"report_id": report_id},
        )


class InvalidReportPeriodError(DomainError):
    """Raised when a reporting period is chronologically invalid."""

    def __init__(self, start_date: str, end_date: str) -> None:
        super().__init__(
            message="Report period start date must be before or equal to end date",
            code="INVALID_REPORT_PERIOD",
            details={"start_date": start_date, "end_date": end_date},
        )


class EmptyDatasetError(DomainError):
    """Raised when an analytical policy requires data but receives none."""

    def __init__(self, dataset_name: str) -> None:
        super().__init__(
            message=f"Dataset '{dataset_name}' cannot be empty for this calculation",
            code="EMPTY_DATASET",
            details={"dataset_name": dataset_name},
        )


class OperationalGatewayAuthError(DomainError):
    """Raised when Reports cannot authenticate outbound calls to Security Gateway."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            message=(
                "Reports cannot authenticate with the operational Security Gateway. "
                f"{reason}"
            ),
            code="OPERATIONAL_GATEWAY_AUTH_FAILED",
            details={"reason": reason},
        )

