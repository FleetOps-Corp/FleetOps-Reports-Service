"""Report API routes.

SAD Traceability: REST entry point for the executive report generation process
in SAD section 10.6.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.responses import Response
from fastapi.security import HTTPBearer

from fleetops_reports.application.dependencies import (
    get_download_report_use_case,
    get_generate_report_use_case,
    get_get_report_use_case,
    get_list_reports_use_case,
)
from fleetops_reports.application.use_cases.download_report import DownloadReportUseCase
from fleetops_reports.application.use_cases.generate_report import GenerateReportUseCase
from fleetops_reports.application.use_cases.get_report import GetReportUseCase
from fleetops_reports.application.use_cases.list_reports import ListReportsUseCase
from fleetops_reports.domain.exceptions import DomainError, ReportNotFoundError
from fleetops_reports.presentation.api.error_mapping import http_status_for_domain_error
from fleetops_reports.presentation.dependencies import get_report_mapper
from fleetops_reports.presentation.mappers.report_mapper import ReportMapper
from fleetops_reports.presentation.schemas.report_schemas import (
    GenerateReportRequest,
    GenerateReportResponse,
    ReportListResponse,
    ReportSummaryResponse,
)

_bearer_scheme = HTTPBearer(
    auto_error=False,
    description=(
        "JWT from Security Gateway POST /auth/login. "
        "Roles allowed: ADMINISTRADOR or EMPLEADO_REPORTES. "
        "Validated by JWTAuthMiddleware."
    ),
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Security(_bearer_scheme)],
)
security_api_router = APIRouter(
    prefix="/api/reports",
    tags=["Reports (Security /api/reports)"],
    dependencies=[Security(_bearer_scheme)],
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
            status_code=http_status_for_domain_error(exc),
            detail=exc.to_dict() if hasattr(exc, "to_dict") else str(exc),
        ) from exc

    # 4. Mapeo de la entidad de dominio de salida al formato JSON de Pydantic
    return mapper.report_to_response(report)


async def list_reports(
    mapper: Annotated[ReportMapper, Depends(get_report_mapper)],
    use_case: Annotated[ListReportsUseCase, Depends(get_list_reports_use_case)],
    sede_operacion: Annotated[str | None, Query()] = None,
    ciudad_operacion: Annotated[str | None, Query()] = None,
) -> ReportListResponse:
    reports = await use_case.execute(mapper.list_query(sede_operacion, ciudad_operacion))
    return mapper.reports_to_list_response(reports)


async def get_report(
    report_id: str,
    mapper: Annotated[ReportMapper, Depends(get_report_mapper)],
    use_case: Annotated[GetReportUseCase, Depends(get_get_report_use_case)],
) -> ReportSummaryResponse:
    try:
        report = await use_case.execute(report_id)
    except ReportNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.to_dict()) from exc
    return mapper.report_to_summary(report)


async def download_report(
    report_id: str,
    use_case: Annotated[DownloadReportUseCase, Depends(get_download_report_use_case)],
) -> Response:
    try:
        result = await use_case.execute(report_id)
    except ReportNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.to_dict()) from exc
    return Response(
        content=result.content,
        media_type=result.content_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )


for report_router in (router, security_api_router):
    report_router.add_api_route(
        "/generate",
        generate_report,
        methods=["POST"],
        response_model=GenerateReportResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Generate consolidated operational report",
    )
    report_router.add_api_route(
        "",
        list_reports,
        methods=["GET"],
        response_model=ReportListResponse,
        summary="List generated reports",
    )
    report_router.add_api_route(
        "/{report_id}",
        get_report,
        methods=["GET"],
        response_model=ReportSummaryResponse,
        summary="Get report metadata",
    )
    report_router.add_api_route(
        "/{report_id}/download",
        download_report,
        methods=["GET"],
        summary="Download report PDF",
    )
