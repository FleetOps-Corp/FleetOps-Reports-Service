"""Metrics endpoint.

SAD Traceability: exposes Prometheus-compatible metrics for the Observability
Pattern listed in the SAD stack and section 10.7.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response

from fleetops_reports.application.dependencies import get_metrics_exporter
from fleetops_reports.application.ports.metrics import MetricsExporter

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def metrics(exporter: MetricsExporter = Depends(get_metrics_exporter)) -> Response:
    content, media_type = exporter.render()
    return Response(content=content, media_type=media_type)
