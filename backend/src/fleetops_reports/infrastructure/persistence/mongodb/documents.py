"""MongoDB document models.

SAD Traceability: stores analytical snapshots, metrics and report metadata in
MongoDB Atlas/local MongoDB per ADR-002.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from beanie import Document


class ReportDocument(Document):
    report_id: str
    title: str
    period: dict[str, str]
    status: str
    document_url: str | None
    kpis: list[dict[str, Any]]
    created_at: datetime

    class Settings:
        name = "reports"

