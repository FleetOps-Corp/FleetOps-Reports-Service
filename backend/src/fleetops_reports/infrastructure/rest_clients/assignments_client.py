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
from fleetops_reports.infrastructure.rest_clients.gateway_http import fetch_gateway_list


class RestAssignmentsClient:
    def __init__(
        self,
        gateway_base_url: str,
        circuit_breaker: CircuitBreaker,
        bearer_token: str | None = None,
    ) -> None:
        self._url = f"{gateway_base_url.rstrip('/')}/asignaciones"
        self._circuit_breaker = circuit_breaker
        self._bearer_token = bearer_token

    async def list_assignments(self) -> list[AssignmentRecord]:
        async def operation() -> list[AssignmentRecord]:
            items = await fetch_gateway_list(self._url, self._bearer_token)
            return [
                AssignmentRecord(
                    assignment_id=item["id"],
                    vehicle_id=item.get("vehiculo_id"),
                    conductor_id=item["conductor_id"],
                    tipo_vehiculo=item["tipo_vehiculo"],
                    start_date=parse_operational_datetime(item["fecha_inicio"]),
                    end_date=(
                        parse_operational_datetime(item["fecha_fin"])
                        if item.get("fecha_fin")
                        else None
                    ),
                )
                for item in items
            ]

        return await self._circuit_breaker.call(operation)
