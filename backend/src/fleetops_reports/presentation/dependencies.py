"""Presentation dependency providers."""

from __future__ import annotations

from functools import lru_cache

from fleetops_reports.config.settings import Settings
from fleetops_reports.presentation.mappers.report_mapper import ReportMapper


@lru_cache
def get_app_settings() -> Settings:
    return Settings()


def get_report_mapper() -> ReportMapper:
    return ReportMapper()
