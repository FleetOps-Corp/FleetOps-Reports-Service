"""Presentation dependency providers."""

from __future__ import annotations

from fleetops_reports.presentation.mappers.report_mapper import ReportMapper


def get_report_mapper() -> ReportMapper:
    return ReportMapper()
