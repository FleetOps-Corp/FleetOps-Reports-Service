"""JWT security helpers for inbound API authentication."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import jwt
from fastapi import HTTPException, status

from fleetops_reports.config.settings import SecuritySettings

logger = logging.getLogger(__name__)

PUBLIC_PATHS = frozenset(
    {
        "/health",
        "/metrics",
        "/docs",
        "/openapi.json",
        "/redoc",
    }
)
ADMINISTRATOR_ROLE = "ADMINISTRADOR"


@lru_cache
def get_security_settings() -> SecuritySettings:
    return SecuritySettings()


def resolve_public_key_path(public_key_path: str) -> Path | None:
    candidate_paths = [Path(public_key_path)]
    if not candidate_paths[0].is_absolute():
        backend_root = Path(__file__).resolve().parents[3]
        project_root = Path(__file__).resolve().parents[4]
        candidate_paths.extend(
            [
                backend_root / public_key_path,
                project_root / public_key_path,
                project_root / "certs" / "public.pem",
            ]
        )

    for candidate_path in candidate_paths:
        if candidate_path.exists():
            return candidate_path
    return None


def load_verification_material(settings: SecuritySettings) -> str:
    algorithm = settings.jwt_algorithm.upper()
    if algorithm.startswith("RS"):
        if not settings.jwt_public_key_path:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
            )
        key_path = resolve_public_key_path(settings.jwt_public_key_path)
        if key_path is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
            )
        return key_path.read_text(encoding="utf-8")

    if not settings.jwt_secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    return settings.jwt_secret_key


def decode_jwt(token: str, settings: SecuritySettings | None = None) -> dict[str, Any]:
    """Decode and validate a JWT using the configured verification material."""
    active_settings = settings or get_security_settings()
    verification_key = load_verification_material(active_settings)
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            verification_key,
            algorithms=[active_settings.jwt_algorithm],
            options={"require": ["sub", "role"]},
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT validation failed: token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    except jwt.InvalidTokenError as exc:
        logger.warning("JWT validation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def ensure_administrator(payload: dict[str, Any]) -> None:
    role = str(payload.get("role", "")).upper()
    if role != ADMINISTRATOR_ROLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator role required.",
        )
