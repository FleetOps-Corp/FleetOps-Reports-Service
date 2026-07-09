"""Assignments REST client.

SAD Traceability: adapter for the Asignaciones service integration required by
ADR-001 and functional processes 10.1 and 10.4, via REST Gateway.
"""

from __future__ import annotations

from fleetops_reports.application.ports.operational_clients import AssignmentRecord
from fleetops_reports.infrastructure.rest_clients.circuit_breaker import CircuitBreaker
from fleetops_reports.infrastructure.rest_clients.datetime_parsing import (
    parse_operational_datetime,
)
from fleetops_reports.infrastructure.rest_clients.field_mapping import (
    get_payload_field,
    get_payload_optional_field,
)
from fleetops_reports.infrastructure.rest_clients.gateway_http import (
    build_gateway_resource_url,
    fetch_gateway_list_optional,
)
from fleetops_reports.infrastructure.rest_clients.gateway_token_provider import (
    GatewayBearerTokenProvider,
)


class RestAssignmentsClient:
    def __init__(
        self,
        gateway_base_url: str,
        circuit_breaker: CircuitBreaker,
        bearer_token: str | None = None,
        *,
        token_provider: GatewayBearerTokenProvider | None = None,
        resource_path: str = "/asignaciones/",
    ) -> None:
        self._url = build_gateway_resource_url(gateway_base_url, resource_path)
        self._circuit_breaker = circuit_breaker
        self._bearer_token = bearer_token
        self._token_provider = token_provider

    async def list_assignments(self) -> list[AssignmentRecord]:
        async def operation() -> list[AssignmentRecord]:
            items = await fetch_gateway_list_optional(
                self._url,
                self._bearer_token,
                token_provider=self._token_provider,
                unavailable_log_message=(
                    "Assignments list endpoint unavailable; continuing without assignments"
                ),
            )
            return [
                AssignmentRecord(
                    assignment_id=get_payload_field(item, "id"),
                    vehicle_id=get_payload_optional_field(item, "vehiculo_id", "vehicle_id"),
                    conductor_id=get_payload_field(item, "conductor_id", "driver_id"),
                    tipo_vehiculo=get_payload_field(item, "tipo_vehiculo", "vehicle_type"),
                    start_date=parse_operational_datetime(
                        get_payload_field(item, "fecha_inicio", "start_date")
                    ),
                    end_date=(
                        parse_operational_datetime(
                            get_payload_field(item, "fecha_fin", "end_date")
                        )
                        if get_payload_field(item, "fecha_fin", "end_date")
                        else None
                    ),
                )
                for item in items
            ]

        return await self._circuit_breaker.call(operation)
