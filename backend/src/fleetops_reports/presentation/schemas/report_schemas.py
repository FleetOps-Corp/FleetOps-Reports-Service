"""Report DTO schemas.

SAD Traceability: DTO Pattern for executive report requests and responses from
SAD section 10.6.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class GenerateReportRequest(BaseModel):
    report_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    start_date: date
    end_date: date
    sede_operacion: str | None = Field(
        default=None,
        description="Optional operation site filter aligned with vehicles sede_operacion.",
    )
    ciudad_operacion: str | None = Field(
        default=None,
        description="Optional city filter aligned with vehicles ciudad_operacion.",
    )


class KPIResponse(BaseModel):
    name: str
    value: float
    unit: str
    source: str


class GenerateReportResponse(BaseModel):
    report_id: str
    title: str
    status: str
    document_url: str | None
    sede_operacion: str | None = None
    ciudad_operacion: str | None = None
    kpis: list[KPIResponse]


class ReportSummaryResponse(BaseModel):
    report_id: str
    title: str
    status: str
    document_url: str | None
    sede_operacion: str | None = None
    ciudad_operacion: str | None = None
    start_date: date
    end_date: date
    created_at: datetime


class ReportListResponse(BaseModel):
    reports: list[ReportSummaryResponse]
    total: int
