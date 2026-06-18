"""Report DTO schemas.

SAD Traceability: DTO Pattern for executive report requests and responses from
SAD section 10.6.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class GenerateReportRequest(BaseModel):
    report_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    start_date: date
    end_date: date


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
    kpis: list[KPIResponse]

