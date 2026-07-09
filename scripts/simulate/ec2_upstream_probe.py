"""Probe upstream Security Gateway routes from EC2 backend context."""

from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request

import jwt


def main() -> int:
    token = os.environ.get("PROBE_TOKEN", "").strip()
    if not token:
        print("PROBE_TOKEN missing")
        return 1

    key_path = os.environ.get("JWT_PUBLIC_KEY_PATH", "/app/certs/public.pem")
    gateway = os.environ.get("OPERATIONAL_GATEWAY_BASE_URL", "http://3.237.75.68:8000").rstrip("/")

    with open(key_path, encoding="utf-8") as handle:
        public_key = handle.read()

    payload = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        options={"require": ["sub", "role"]},
    )
    print(f"decode_ok role={payload.get('role')}")

    paths = (
        "/vehiculos/",
        "/api/vehicles/",
        "/asignaciones/",
        "/api/incidents/",
        "/api/v1/mantenimientos/",
        "/mantenimiento/",
    )
    for path in paths:
        request = urllib.request.Request(
            f"{gateway}{path}",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = response.read()
                print(f"{path} -> {response.status} bytes={len(body)}")
        except urllib.error.HTTPError as exc:
            detail = exc.read(120).decode("utf-8", errors="replace")
            print(f"{path} -> HTTP {exc.code} {detail}")
        except OSError as exc:
            print(f"{path} -> ERR {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
