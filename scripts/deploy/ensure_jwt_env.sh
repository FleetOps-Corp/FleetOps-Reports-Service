#!/usr/bin/env bash
# Ensure inbound JWT variables exist in the Reports .env on the target host.
# Usage (on EC2, from /opt/fleetops-reports):
#   export JWT_SECRET_KEY='<same value as FleetOps Security Service>'
#   ./scripts/deploy/ensure_jwt_env.sh .env
set -euo pipefail

ENV_FILE="${1:-.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Env file not found: $ENV_FILE" >&2
  exit 1
fi

grep -q '^JWT_ALGORITHM=' "$ENV_FILE" || echo 'JWT_ALGORITHM=HS256' >> "$ENV_FILE"

if ! grep -q '^JWT_SECRET_KEY=' "$ENV_FILE"; then
  if [[ -z "${JWT_SECRET_KEY:-}" ]]; then
    echo "JWT_SECRET_KEY is not set. Export the Security Service secret before running." >&2
    exit 1
  fi
  printf 'JWT_SECRET_KEY=%s\n' "$JWT_SECRET_KEY" >> "$ENV_FILE"
fi

echo "JWT variables present in $ENV_FILE"
