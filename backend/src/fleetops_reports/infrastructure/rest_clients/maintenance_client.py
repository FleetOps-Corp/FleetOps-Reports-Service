"""Maintenance REST client.

SAD Traceability: adapter for the Mantenimientos service integration required by
ADR-001 and functional processes 10.1 and 10.4, via REST Gateway.
"""

from __future__ import annotations

import httpx

from fleetops_reports.application.ports.operational_clients import MaintenanceRecord
from fleetops_reports.infrastructure.rest_clients.circuit_breaker import CircuitBreaker
from fleetops_reports.infrastructure.rest_clients.datetime_parsing import parse_utc_datetime

_MAINTENANCE_TYPE_MAP = {0: "CORRECTIVO", 1: "PREVENTIVO"}


class RestMaintenanceClient:
    def __init__(self, gateway_base_url: str, circuit_breaker: CircuitBreaker) -> None:
        self._url = f"{gateway_base_url}/mantenimientos"
        self._circuit_breaker = circuit_breaker

    async def list_maintenance(self) -> list[MaintenanceRecord]:
        async def operation() -> list[MaintenanceRecord]:
            async with httpx.AsyncClient() as client:
                response = await client.get(self._url)
                response.raise_for_status()
                return [
                    MaintenanceRecord(
                        vehicle_id=item["id_vehiculo"],
                        maintenance_type=_MAINTENANCE_TYPE_MAP.get(
                            item["tipo_mantenimiento"], "DESCONOCIDO"
                        ),
                        started_at=parse_utc_datetime(item["fecha_inicio_mantenimiento"]),
                        finished_at=(
                            parse_utc_datetime(item["fecha_fin_mantenimiento"])
                            if item.get("fecha_fin_mantenimiento")
                            else None
                        ),
                    )
                    for item in response.json()
                ]

        return await self._circuit_breaker.call(operation)
