#!/usr/bin/env python3
"""Download a report PDF from MinIO to stdout or a file (deployed host helper)."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from fleetops_reports.composition.wiring import (
    _build_download_report_use_case,
    configure_application,
    get_settings,
)
from fleetops_reports.infrastructure.persistence.mongodb.mongo_client import init_mongodb


async def _download(report_id: str, output_path: str) -> None:
    configure_application()
    settings = get_settings()
    client = await init_mongodb(settings)
    try:
        result = await _build_download_report_use_case(settings).execute(report_id)
        Path(output_path).write_bytes(result.content)
        print(f"Wrote {output_path} bytes={len(result.content)}")
    finally:
        await client.close()


if __name__ == "__main__":
    report_id = sys.argv[1] if len(sys.argv) > 1 else "rep-ref-bogota-202605"
    output = sys.argv[2] if len(sys.argv) > 2 else f"/tmp/{report_id}.pdf"
    asyncio.run(_download(report_id, output))
