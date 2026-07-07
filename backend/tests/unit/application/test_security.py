"""Security helper tests."""

import jwt
import pytest
from fastapi import HTTPException

from fleetops_reports.config.security import decode_jwt, get_security_settings
from fleetops_reports.config.settings import SecuritySettings


def test_decode_jwt_with_hs256_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-minimum-32-characters")
    monkeypatch.delenv("JWT_PUBLIC_KEY_PATH", raising=False)
    get_security_settings.cache_clear()

    token = jwt.encode(
        {"sub": "user-1", "role": "ADMINISTRADOR"},
        "test-secret-key-minimum-32-characters",
        algorithm="HS256",
    )
    payload = decode_jwt(token)
    assert payload["sub"] == "user-1"


def test_decode_jwt_rejects_invalid_role_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-minimum-32-characters")
    get_security_settings.cache_clear()

    token = jwt.encode(
        {"sub": "user-1"},
        "test-secret-key-minimum-32-characters",
        algorithm="HS256",
    )
    with pytest.raises(HTTPException):
        decode_jwt(token)


def test_load_verification_material_requires_secret_for_hs256(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    get_security_settings.cache_clear()
    settings = SecuritySettings()
    with pytest.raises(HTTPException):
        from fleetops_reports.config.security import load_verification_material

        load_verification_material(settings)
