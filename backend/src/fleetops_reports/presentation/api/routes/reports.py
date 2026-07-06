"""Report API routes.

SAD Traceability: REST entry point for the executive report generation process
in SAD section 10.6.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from fleetops_reports.application.dependencies import get_generate_report_use_case
from fleetops_reports.application.use_cases.generate_report import GenerateReportUseCase
from fleetops_reports.domain.exceptions import DomainError
from fleetops_reports.presentation.dependencies import get_report_mapper
from fleetops_reports.presentation.mappers.report_mapper import ReportMapper
from fleetops_reports.presentation.schemas.report_schemas import (
    GenerateReportRequest,
    GenerateReportResponse,
)

# Cambiamos el tag a mayúscula 'Reports' para mejorar la visualización en Swagger / OpenAPI Docs
router = APIRouter(prefix="/reports", tags=["Reports"])
gateway_router = APIRouter(prefix="/reportes", tags=["Reports (Gateway)"])


@router.post(
    "/generate",
    response_model=GenerateReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar Reporte Operativo Consolidado",
    description=(
        "Orquesta y consolida los datos distribuidos de vehículos, "
        "asignaciones, incidentes y mantenimientos."
    ),
)

async def generate_report(
    request: GenerateReportRequest,
    use_case: Annotated[GenerateReportUseCase, Depends(get_generate_report_use_case)],
    mapper: Annotated[ReportMapper, Depends(get_report_mapper)],
) -> GenerateReportResponse:

    # 1. Transformamos la petición HTTP entrante a un comando de la capa de aplicación
    command = mapper.request_to_command(request)

    try:
        # 2. Ejecución asíncrona del caso de uso cruzando los 4 microservices bajo ADR-005
        report = await use_case.execute(command)

    except DomainError as exc:
        # 3. Captura limpia de errores de lógica de negocio o fallos concurrentes controlados
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.to_dict() if hasattr(exc, "to_dict") else str(exc),
        ) from exc

    # 4. Mapeo de la entidad de dominio de salida al formato JSON de Pydantic
    return mapper.report_to_response(report)


gateway_router.add_api_route(
    "/generate",
    generate_report,
    methods=["POST"],
    response_model=GenerateReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar Reporte (alias Security Gateway /reportes)",
    description="Alias compatible con el prefijo /reportes expuesto por FleetOps Security Gateway.",
)
