"""Assignments REST client.

SAD Traceability: adapter for the Asignaciones service integration required by
ADR-001 and functional processes 10.1 and 10.4, via REST Gateway.
"""

from __future__ import annotations

from datetime import datetime

import httpx

from fleetops_reports.application.ports.operational_clients import AssignmentRecord
from fleetops_reports.infrastructure.rest_clients.circuit_breaker import CircuitBreaker


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class RestAssignmentsClient:
    def __init__(self, gateway_base_url: str, circuit_breaker: CircuitBreaker) -> None:
        self._url = f"{gateway_base_url}/asignaciones"
        self._circuit_breaker = circuit_breaker

    async def list_assignments(self) -> list[AssignmentRecord]:
        async def operation() -> list[AssignmentRecord]:
            async with httpx.AsyncClient() as client:
                response = await client.get(self._url)
                response.raise_for_status()
                return [
                    AssignmentRecord(
                        assignment_id=item["id"],
                        vehicle_id=item.get("vehiculo_id"),
                        conductor_id=item["conductor_id"],
                        tipo_vehiculo=item["tipo_vehiculo"],
                        start_date=_parse_dt(item["fecha_inicio"]),
                        end_date=_parse_dt(item["fecha_fin"]) if item.get("fecha_fin") else None,
                    )
                    for item in response.json()
                ]

        return await self._circuit_breaker.call(operation)
