"""Build production .env for EC2 deployment (writes local temp file only)."""

from __future__ import annotations

import secrets
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PEM = ROOT.parent / "fleetops-reports-key.pem"
HOST = "ubuntu@ec2-18-217-5-127.us-east-2.compute.amazonaws.com"
OUT = ROOT / ".env.ec2.deploy.tmp"


def _parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key, value = stripped.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def _normalize_atlas_uri(uri: str) -> str:
    if "mongodb.net/?" in uri:
        return uri.replace(
            "mongodb.net/?",
            "mongodb.net/fleetops_reports?retryWrites=true&w=majority&",
        )
    if "mongodb.net/" in uri.split("@")[-1] and "/fleetops_reports" not in uri:
        return uri.replace("mongodb.net/", "mongodb.net/fleetops_reports?", 1)
    return uri


def main() -> int:
    local = _parse_env(ROOT / ".env")
    remote_raw = subprocess.check_output(
        [
            "ssh",
            "-i",
            str(PEM),
            "-o",
            "ConnectTimeout=25",
            HOST,
            "grep -E '^(MINIO_ACCESS_KEY|MINIO_SECRET_KEY)=' /opt/fleetops-reports/.env || true",
        ],
        text=True,
    )
    remote: dict[str, str] = {}
    for line in remote_raw.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            remote[key.strip()] = value.strip()

    mongo_uri = _normalize_atlas_uri(local.get("MONGODB_URI", ""))
    content = f"""GATEWAY_HTTP_PORT=8081
APP_ENVIRONMENT=production
LOG_LEVEL=INFO
LOG_FILE_PATH=/var/log/fleetops-reports/app.log
MONGODB_URI={mongo_uri}
MONGODB_DATABASE={local.get("MONGODB_DATABASE", "fleetops_reports")}
MONGO_INITDB_ROOT_USERNAME=unused
MONGO_INITDB_ROOT_PASSWORD=unused
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY={remote.get("MINIO_ACCESS_KEY", secrets.token_hex(16))}
MINIO_SECRET_KEY={remote.get("MINIO_SECRET_KEY", secrets.token_hex(32))}
MINIO_SECURE=false
MINIO_REPORTS_BUCKET=fleetops-reports
MINIO_GRAPHS_BUCKET=fleetops-graphs
OPERATIONAL_GATEWAY_BASE_URL={local.get("OPERATIONAL_GATEWAY_BASE_URL", "http://host.docker.internal:8000")}
OPERATIONAL_GATEWAY_BEARER_TOKEN={local.get("OPERATIONAL_GATEWAY_BEARER_TOKEN", "")}
CIRCUIT_BREAKER_FAILURE_THRESHOLD=3
CIRCUIT_BREAKER_RECOVERY_SECONDS=30
TEMPLATES_DIR=
GRAFANA_HTTP_PORT=3000
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=unused
"""
    OUT.write_text(content, encoding="utf-8")
    print("ENV_READY")
    return 0


if __name__ == "__main__":
    sys.exit(main())
