"""Vehicles gRPC client.

SAD Traceability: adapter for the Vehículos service integration required by
ADR-001 and functional processes 10.1 and 10.4.
"""

from __future__ import annotations

import grpc

# Importación de stubs autogenerados del microservicio FleetOps Vehículos
from fleetops_reports.domain.models.vehicle import Vehicle
from fleetops_reports.infrastructure.grpc_clients.circuit_breaker import CircuitBreaker
from fleetops_reports.infrastructure.grpc_clients.protos import (
    vehiculos_pb2,
    vehiculos_pb2_grpc,
)


class GrpcVehiclesClient:
    def __init__(self, target: str, circuit_breaker: CircuitBreaker) -> None:
        self._target = target
        self._circuit_breaker = circuit_breaker
        # Apertura de canal asíncrono gRPC e inicialización del Stub contractual
        self._channel = grpc.aio.insecure_channel(self._target)
        self._stub = vehiculos_pb2_grpc.VehiclesServiceStub(self._channel)

    async def list_vehicles(self) -> list[Vehicle]:

        async def operation() -> list[Vehicle]:
            # Construcción de la petición para obtener todo el catálogo de vehículos activos
            request = vehiculos_pb2.ListVehiclesRequest(only_active=True)

            # Ejecución concurrente asíncrona sobre la topología de red
            response = await self._stub.GetAllVehicles(request)

            vehicle_list: list[Vehicle] = []
            for item in response.vehicles:
                # Mapeamos rigurosamente cada registro de red a la entidad de Dominio
                vehicle_list.append(
                    Vehicle(
                        id_vehiculo=str(item.id_vehiculo),  # UUID v4
                        numero_placa=str(item.numero_placa),  # Placa real normalizada
                        estado_vehiculo=str(
                            item.estado_vehiculo
                        ),  # 'DISPONIBLE' / 'EN_MANTENIMIENTO'
                        ciudad_operacion=str(
                            item.ciudad_operacion
                        ),  # Ciudad de operación
                        marca=str(item.marca),  # Fabricante
                        modelo=str(item.modelo),  # Modelo
                    )
                )
            return vehicle_list

        # El Circuit Breaker envuelve la llamada de red,
        # mitigando fallos en cascada si el servicio cae
        return await self._circuit_breaker.call(operation)

    async def close(self) -> None:
        """Cierre ordenado de los canales de red activos."""
        await self._channel.close()
