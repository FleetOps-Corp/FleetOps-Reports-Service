"""Report API routes.

SAD Traceability: REST entry point for the executive report generation process
in SAD section 10.6.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response

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
from fleetops_reports.presentation.dependencies import get_report_mapper
from fleetops_reports.presentation.mappers.report_mapper import ReportMapper
from fleetops_reports.presentation.schemas.report_schemas import (
    GenerateReportRequest,
    GenerateReportResponse,
    ReportListResponse,
    ReportSummaryResponse,
)

router = APIRouter(prefix="/reports", tags=["Reports"])
gateway_router = APIRouter(prefix="/reportes", tags=["Reports (Gateway)"])
security_api_router = APIRouter(
    prefix="/api/reports",
    tags=["Reports (Security /api/reports)"],
)


async def generate_report(
    request: GenerateReportRequest,
    use_case: Annotated[GenerateReportUseCase, Depends(get_generate_report_use_case)],
    mapper: Annotated[ReportMapper, Depends(get_report_mapper)],
) -> GenerateReportResponse:
    command = mapper.request_to_command(request)
    try:
        report = await use_case.execute(command)
    except DomainError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.to_dict() if hasattr(exc, "to_dict") else str(exc),
        ) from exc
    return mapper.report_to_response(report)


async def list_reports(
    mapper: Annotated[ReportMapper, Depends(get_report_mapper)],
    use_case: Annotated[ListReportsUseCase, Depends(get_list_reports_use_case)],
    sede_operacion: Annotated[str | None, Query()] = None,
) -> ReportListResponse:
    reports = await use_case.execute(mapper.list_query(sede_operacion))
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


router.add_api_route(
    "/generate",
    generate_report,
    methods=["POST"],
    response_model=GenerateReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar Reporte Operativo Consolidado",
)
router.add_api_route(
    "",
    list_reports,
    methods=["GET"],
    response_model=ReportListResponse,
    summary="Listar reportes generados",
)
router.add_api_route(
    "/{report_id}",
    get_report,
    methods=["GET"],
    response_model=ReportSummaryResponse,
    summary="Consultar metadatos de un reporte",
)
router.add_api_route(
    "/{report_id}/download",
    download_report,
    methods=["GET"],
    summary="Descargar PDF de un reporte",
)

for alias_router, label in (
    (gateway_router, "/reportes"),
    (security_api_router, "/api/reports"),
):
    alias_router.add_api_route(
        "/generate",
        generate_report,
        methods=["POST"],
        response_model=GenerateReportResponse,
        status_code=status.HTTP_201_CREATED,
        summary=f"Generar Reporte (alias Security Gateway {label})",
    )
    alias_router.add_api_route(
        "",
        list_reports,
        methods=["GET"],
        response_model=ReportListResponse,
        summary=f"Listar reportes (alias Security Gateway {label})",
    )
    alias_router.add_api_route(
        "/{report_id}",
        get_report,
        methods=["GET"],
        response_model=ReportSummaryResponse,
        summary=f"Consultar reporte (alias Security Gateway {label})",
    )
    alias_router.add_api_route(
        "/{report_id}/download",
        download_report,
        methods=["GET"],
        summary=f"Descargar PDF (alias Security Gateway {label})",
    )
