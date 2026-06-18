"""Report API routes.

SAD Traceability: REST entry point for the executive report generation process
in SAD section 10.6.
"""

from __future__ import annotations

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

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=GenerateReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    request: GenerateReportRequest,
    use_case: GenerateReportUseCase = Depends(get_generate_report_use_case),
    mapper: ReportMapper = Depends(get_report_mapper),
) -> GenerateReportResponse:
    command = mapper.request_to_command(request)
    try:
        report = await use_case.execute(command)
    except DomainError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.to_dict(),
        ) from exc
    return mapper.report_to_response(report)
