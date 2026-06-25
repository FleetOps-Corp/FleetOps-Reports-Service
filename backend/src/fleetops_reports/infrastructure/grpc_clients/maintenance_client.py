"""Maintenance gRPC client.

SAD Traceability: adapter for the Mantenimientos service integration required
by ADR-001 and maintenance efficiency process 10.2.
"""

from __future__ import annotations

from datetime import UTC, datetime

import grpc

from fleetops_reports.application.ports.operational_clients import MaintenanceRecord
from fleetops_reports.infrastructure.grpc_clients.circuit_breaker import CircuitBreaker

# Importación de stubs generados por el comando 'make proto' para Mantenimientos
from fleetops_reports.infrastructure.grpc_clients.protos import (
    mantenimientos_pb2,
    mantenimientos_pb2_grpc,
)


class GrpcMaintenanceClient:
    def __init__(self, target: str, circuit_breaker: CircuitBreaker) -> None:
        self._target = target
        self._circuit_breaker = circuit_breaker
        # Inicialización del canal asíncrono gRPC
        self._channel = grpc.aio.insecure_channel(self._target)
        self._stub = mantenimientos_pb2_grpc.MantenimientosServiceStub(self._channel)

    async def list_maintenance(self) -> list[MaintenanceRecord]:

        async def operation() -> list[MaintenanceRecord]:
            # Petición para listar el histórico de órdenes del taller
            request = mantenimientos_pb2.ListMaintenanceRequest()

            # Ejecución de llamada RPC asíncrona a través de la red
            response = await self._stub.ListVehicleMaintenances(request)

            records: list[MaintenanceRecord] = []
            for item in response.maintenances:
                # Conversión de las fechas ISO 8601 strings del servicio a datetime de Python
                started_dt = datetime.fromisoformat(
                    item.fecha_inicio_mantenimiento
                ).replace(tzinfo=UTC)

                finished_dt = None
                if item.fecha_fin_mantenimiento:
                    finished_dt = datetime.fromisoformat(
                        item.fecha_fin_mantenimiento
                    ).replace(tzinfo=UTC)

                # Traducción del campo tipo_mantenimiento (SMALLINT/uint8)
                # Mapeo: 0 -> CORRECTIVO, 1 -> PREVENTIVO
                type_str = (
                    "PREVENTIVO" if item.tipo_mantenimiento == 1 else "CORRECTIVO"
                )

                records.append(
                    MaintenanceRecord(
                        vehicle_id=str(item.id_vehiculo),  # UUID del vehículo
                        maintenance_type=type_str,  # 'CORRECTIVO' o 'PREVENTIVO'
                        started_at=started_dt,  # Inicio formal de operaciones
                        finished_at=finished_dt,  # Fin o None si sigue activo
                    )
                )
            return records

        # Delegación segura de la operación al Circuit Breaker
        return await self._circuit_breaker.call(operation)

    async def close(self) -> None:
        """Cierre ordenado de recursos de red."""
        await self._channel.close()
