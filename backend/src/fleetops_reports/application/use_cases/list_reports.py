"""List reports use case."""

from __future__ import annotations

from dataclasses import dataclass

from fleetops_reports.application.ports.analytics_repository import AnalyticsRepository
from fleetops_reports.domain.models.report import Report


@dataclass(frozen=True)
class ListReportsQuery:
    sede_operacion: str | None = None
    ciudad_operacion: str | None = None


class ListReportsUseCase:
    def __init__(self, repository: AnalyticsRepository) -> None:
        self._repository = repository

    async def execute(self, query: ListReportsQuery) -> list[Report]:
        return await self._repository.list_reports(
            sede_operacion=query.sede_operacion,
            ciudad_operacion=query.ciudad_operacion,
        )
