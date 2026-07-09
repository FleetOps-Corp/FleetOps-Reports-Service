#!/usr/bin/env python3
"""Seed the reference fixture report into MongoDB and MinIO on a deployed host."""

from __future__ import annotations

import asyncio
import sys
from datetime import date
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2] / "backend"
SRC = BACKEND / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fleetops_reports.application.use_cases.generate_report import (  # noqa: E402
    GenerateReportCommand,
)
from fleetops_reports.composition.wiring import (  # noqa: E402
    _build_fixture_generate_report_use_case,
    get_settings,
)


REFERENCE_REPORT_ID = "rep-ref-bogota-202605"


async def _seed() -> None:
    settings = get_settings()
    if not settings.fixture_reports_enabled:
        raise SystemExit("FIXTURE_REPORTS_ENABLED must be true to seed reference report.")

    use_case = _build_fixture_generate_report_use_case(settings)
    report = await use_case.execute(
        GenerateReportCommand(
            report_id=REFERENCE_REPORT_ID,
            title="FleetOps Executive Report — Fixture Reference (Bogotá)",
            period=__import__(
                "fleetops_reports.domain.value_objects.report_period", fromlist=["ReportPeriod"]
            ).ReportPeriod(start_date=date(2026, 5, 1), end_date=date(2026, 5, 31)),
            ciudad_operacion="Bogotá",
        )
    )
    print(f"Seeded report_id={report.report_id} status={report.status} pdf={report.document_url}")


def main() -> int:
    asyncio.run(_seed())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
