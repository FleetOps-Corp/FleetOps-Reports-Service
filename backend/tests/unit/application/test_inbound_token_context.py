"""Inbound JWT context tests."""

from fleetops_reports.application.inbound_token_context import (
    get_inbound_bearer_token,
    reset_inbound_bearer_token,
    set_inbound_bearer_token,
)


def test_inbound_bearer_token_context_roundtrip() -> None:
    assert get_inbound_bearer_token() is None

    token = set_inbound_bearer_token("  bearer-value  ")
    assert get_inbound_bearer_token() == "bearer-value"
    reset_inbound_bearer_token(token)
    assert get_inbound_bearer_token() is None


def test_inbound_bearer_token_normalizes_blank_values() -> None:
    token = set_inbound_bearer_token("   ")
    try:
        assert get_inbound_bearer_token() is None
    finally:
        reset_inbound_bearer_token(token)
