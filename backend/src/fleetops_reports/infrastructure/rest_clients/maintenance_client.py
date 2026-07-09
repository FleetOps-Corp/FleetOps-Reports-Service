"""Maintenance REST client.

SAD Traceability: adapter for the Mantenimiento service integration required by
ADR-001 and functional processes 10.1 and 10.4, via REST Gateway.
"""

from __future__ import annotations

from typing import Any

from fleetops_reports.application.ports.operational_clients import MaintenanceRecord
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
    fetch_gateway_list,
)
from fleetops_reports.infrastructure.rest_clients.gateway_token_provider import (
    GatewayBearerTokenProvider,
)

_MAINTENANCE_TYPE_MAP = {0: "CORRECTIVO", 1: "PREVENTIVO"}


def _map_maintenance_type(value: int | str) -> str:
    if isinstance(value, str):
        return value.upper()
    return _MAINTENANCE_TYPE_MAP.get(value, "DESCONOCIDO")


def _resolve_maintenance_type(item: dict[str, Any]) -> int | str:
    if "tipo_mantenimiento" in item and item["tipo_mantenimiento"] is not None:
        raw = item["tipo_mantenimiento"]
        return raw if isinstance(raw, int | str) else "DESCONOCIDO"
    if "tipo" in item and item["tipo"] is not None:
        raw = item["tipo"]
        return raw if isinstance(raw, int | str) else "DESCONOCIDO"
    return "DESCONOCIDO"


class RestMaintenanceClient:
    def __init__(
        self,
        gateway_base_url: str,
        circuit_breaker: CircuitBreaker,
        bearer_token: str | None = None,
        *,
        token_provider: GatewayBearerTokenProvider | None = None,
        resource_path: str = "/api/v1/mantenimientos/",
    ) -> None:
        self._url = build_gateway_resource_url(gateway_base_url, resource_path)
        self._circuit_breaker = circuit_breaker
        self._bearer_token = bearer_token
        self._token_provider = token_provider

    async def list_maintenance(self) -> list[MaintenanceRecord]:
        async def operation() -> list[MaintenanceRecord]:
            items = await fetch_gateway_list(
                self._url,
                self._bearer_token,
                token_provider=self._token_provider,
            )
            return [
                MaintenanceRecord(
                    vehicle_id=get_payload_field(item, "id_vehiculo", "vehicle_id"),
                    maintenance_type=_map_maintenance_type(_resolve_maintenance_type(item)),
                    started_at=parse_operational_datetime(
                        get_payload_field(
                            item,
                            "fecha_inicio_mantenimiento",
                            "creado_en",
                            "fecha_de_mantenimiento",
                        )
                    ),
                    finished_at=(
                        parse_operational_datetime(finished_at)
                        if (finished_at := get_payload_optional_field(
                            item,
                            "fecha_fin_mantenimiento",
                            "completado_en",
                        ))
                        else None
                    ),
                )
                for item in items
            ]

        return await self._circuit_breaker.call(operation)
