"""FastAPI application entry point.

SAD Traceability: presentation entry for FleetOps Reports, exposing REST APIs
and metrics as described in SAD sections 6, 10.6, 10.7 and 11.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from fleetops_reports.composition.wiring import (
    configure_application,
    get_settings,
)
from fleetops_reports.infrastructure.observability.logging import configure_logging
from fleetops_reports.infrastructure.persistence.mongodb.mongo_client import (
    init_mongodb,
)
from fleetops_reports.presentation.api.middleware import register_auth_middleware
from fleetops_reports.presentation.api.routes import health, metrics, reports

configure_application()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_file_path)
    app.state.mongodb_client = await init_mongodb(settings)
    try:
        yield
    finally:
        app.state.mongodb_client.close()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    register_auth_middleware(app)
    app.include_router(health.router)
    app.include_router(metrics.router)
    app.include_router(reports.router)
    app.include_router(reports.gateway_router)
    app.include_router(reports.security_api_router)
    return app


app = create_app()
