"""MongoDB analytics repository.

SAD Traceability: concrete Repository Pattern adapter for report metadata,
KPIs and snapshots in ADR-002.
"""

from __future__ import annotations

from datetime import date

from fleetops_reports.domain.models.kpi import KPI
from fleetops_reports.domain.models.report import Report
from fleetops_reports.domain.value_objects.metric import Metric
from fleetops_reports.domain.value_objects.report_period import ReportPeriod
from fleetops_reports.infrastructure.persistence.mongodb.documents import ReportDocument


def _document_to_report(document: ReportDocument) -> Report:
    return Report(
        report_id=document.report_id,
        title=document.title,
        period=ReportPeriod(
            start_date=date.fromisoformat(document.period["start_date"]),
            end_date=date.fromisoformat(document.period["end_date"]),
        ),
        kpis=[
            KPI.create_now(
                name=item["name"],
                metric=Metric(name=item["metric"], value=item["value"], unit=item["unit"]),
                source=item["source"],
            )
            for item in document.kpis
        ],
        status=document.status,
        document_url=document.document_url,
        sede_operacion=document.sede_operacion,
        ciudad_operacion=document.ciudad_operacion,
        created_at=document.created_at,
    )


class MongoAnalyticsRepository:
    async def save_report(self, report: Report) -> Report:
        document = ReportDocument(
            report_id=report.report_id,
            title=report.title,
            period={
                "start_date": report.period.start_date.isoformat(),
                "end_date": report.period.end_date.isoformat(),
            },
            status=report.status,
            document_url=report.document_url,
            sede_operacion=report.sede_operacion,
            ciudad_operacion=report.ciudad_operacion,
            kpis=[
                {
                    "name": kpi.name,
                    "metric": kpi.metric.name,
                    "value": kpi.metric.value,
                    "unit": kpi.metric.unit,
                    "source": kpi.source,
                    "calculated_at": kpi.calculated_at,
                }
                for kpi in report.kpis
            ],
            created_at=report.created_at,
        )
        await ReportDocument.find_one(ReportDocument.report_id == report.report_id).delete()
        await document.insert()
        return report

    async def get_report(self, report_id: str) -> Report | None:
        document = await ReportDocument.find_one(ReportDocument.report_id == report_id)
        if document is None:
            return None
        return _document_to_report(document)

    async def list_reports(
        self,
        sede_operacion: str | None = None,
        ciudad_operacion: str | None = None,
    ) -> list[Report]:
        documents = await ReportDocument.find_all().sort("-created_at").to_list()
        if sede_operacion:
            normalized = sede_operacion.strip().casefold()
            documents = [
                document
                for document in documents
                if (document.sede_operacion or "").strip().casefold() == normalized
            ]
        if ciudad_operacion:
            normalized = ciudad_operacion.strip().casefold()
            documents = [
                document
                for document in documents
                if (document.ciudad_operacion or "").strip().casefold() == normalized
            ]
        return [_document_to_report(document) for document in documents]
