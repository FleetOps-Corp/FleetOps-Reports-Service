"""Maintenance REST client.

SAD Traceability: adapter for the Mantenimiento service integration required by
ADR-001 and functional processes 10.1 and 10.4, via REST Gateway.
"""

from __future__ import annotations

from fleetops_reports.application.ports.operational_clients import MaintenanceRecord
from fleetops_reports.infrastructure.rest_clients.circuit_breaker import CircuitBreaker
from fleetops_reports.infrastructure.rest_clients.datetime_parsing import (
    parse_operational_datetime,
)
from fleetops_reports.infrastructure.rest_clients.gateway_http import fetch_gateway_list

_MAINTENANCE_TYPE_MAP = {0: "CORRECTIVO", 1: "PREVENTIVO"}


def _map_maintenance_type(value: int | str) -> str:
    if isinstance(value, str):
        return value.upper()
    return _MAINTENANCE_TYPE_MAP.get(value, "DESCONOCIDO")


class RestMaintenanceClient:
    def __init__(
        self,
        gateway_base_url: str,
        circuit_breaker: CircuitBreaker,
        bearer_token: str | None = None,
    ) -> None:
        # Security Gateway route prefix: /mantenimiento/**
        self._url = f"{gateway_base_url.rstrip('/')}/mantenimiento"
        self._circuit_breaker = circuit_breaker
        self._bearer_token = bearer_token

    async def list_maintenance(self) -> list[MaintenanceRecord]:
        async def operation() -> list[MaintenanceRecord]:
            items = await fetch_gateway_list(self._url, self._bearer_token)
            return [
                MaintenanceRecord(
                    vehicle_id=item["id_vehiculo"],
                    maintenance_type=_map_maintenance_type(item["tipo_mantenimiento"]),
                    started_at=parse_operational_datetime(
                        item["fecha_inicio_mantenimiento"]
                    ),
                    finished_at=(
                        parse_operational_datetime(item["fecha_fin_mantenimiento"])
                        if item.get("fecha_fin_mantenimiento")
                        else None
                    ),
                )
                for item in items
            ]

        return await self._circuit_breaker.call(operation)
