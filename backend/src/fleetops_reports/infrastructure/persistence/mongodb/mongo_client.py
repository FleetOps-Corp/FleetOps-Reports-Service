"""MongoDB client initialization.

SAD Traceability: connects FleetOps Reports to MongoDB Atlas in production and
local MongoDB in development/testing, preserving ADR-002.
"""

from __future__ import annotations

from beanie import init_beanie
from pymongo import AsyncMongoClient

from fleetops_reports.config.settings import Settings
from fleetops_reports.infrastructure.persistence.mongodb.documents import ReportDocument


async def init_mongodb(settings: Settings) -> AsyncMongoClient:
    client: AsyncMongoClient = AsyncMongoClient(settings.mongodb_uri)
    await init_beanie(
        database=client[settings.mongodb_database],
        document_models=[ReportDocument],
    )
    return client

