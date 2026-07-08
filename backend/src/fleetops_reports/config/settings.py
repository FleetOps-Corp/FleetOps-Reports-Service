"""Application settings.

SAD Traceability: keeps ports, credentials and environment-specific values
externalized through environment variables per prompt hard constraints.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    )


class SecuritySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[4] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_public_key_path: str | None = Field(default=None, alias="JWT_PUBLIC_KEY_PATH")
    jwt_secret_key: str | None = Field(default=None, alias="JWT_SECRET_KEY")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[4] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    app_name: str = "FleetOps Reports"
    app_environment: str = Field(alias="APP_ENVIRONMENT")
    log_level: str = Field(alias="LOG_LEVEL")
    log_file_path: str | None = Field(default=None, alias="LOG_FILE_PATH")

    mongodb_uri: str = Field(alias="MONGODB_URI")
    mongodb_database: str = Field(alias="MONGODB_DATABASE")

    minio_endpoint: str = Field(alias="MINIO_ENDPOINT")
    minio_access_key: str = Field(alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(alias="MINIO_SECRET_KEY")
    minio_secure: bool = Field(alias="MINIO_SECURE")
    minio_reports_bucket: str = Field(alias="MINIO_REPORTS_BUCKET")
    minio_graphs_bucket: str = Field(alias="MINIO_GRAPHS_BUCKET")

    operational_gateway_base_url: str = Field(alias="OPERATIONAL_GATEWAY_BASE_URL")
    operational_gateway_bearer_token: str | None = Field(
        default=None, alias="OPERATIONAL_GATEWAY_BEARER_TOKEN"
    )
    operational_vehicles_path: str = Field(
        default="/vehiculos/",
        alias="OPERATIONAL_VEHICLES_PATH",
    )
    operational_assignments_path: str = Field(
        default="/asignaciones/",
        alias="OPERATIONAL_ASSIGNMENTS_PATH",
    )
    operational_incidents_path: str = Field(
        default="/incidentes/",
        alias="OPERATIONAL_INCIDENTS_PATH",
    )
    operational_maintenance_path: str = Field(
        default="/mantenimiento/",
        alias="OPERATIONAL_MAINTENANCE_PATH",
    )

    circuit_breaker_failure_threshold: int = Field(
        alias="CIRCUIT_BREAKER_FAILURE_THRESHOLD"
    )
    circuit_breaker_recovery_seconds: int = Field(
        alias="CIRCUIT_BREAKER_RECOVERY_SECONDS"
    )

    templates_dir: str | None = Field(default=None, alias="TEMPLATES_DIR")

    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_public_key_path: str | None = Field(default=None, alias="JWT_PUBLIC_KEY_PATH")
    jwt_secret_key: str | None = Field(default=None, alias="JWT_SECRET_KEY")
