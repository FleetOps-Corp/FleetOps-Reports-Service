#!/usr/bin/env bash
# Apply Security Gateway integration settings on the Reports EC2 host.
# Usage (on EC2 from /opt/fleetops-reports):
#   export SECURITY_GATEWAY_URL='http://3.237.75.68:8000'
#   export OPERATIONAL_GATEWAY_BEARER_TOKEN='<JWT from Security /auth/login>'
#   # or prefer service-account auto login:
#   export OPERATIONAL_GATEWAY_SERVICE_EMAIL='reports-service@example.com'
#   export OPERATIONAL_GATEWAY_SERVICE_PASSWORD='<password>'
#   ./scripts/deploy/configure_ec2_security_integration.sh .env
set -euo pipefail

ENV_FILE="${1:-.env}"
SECURITY_GATEWAY_URL="${SECURITY_GATEWAY_URL:-http://3.237.75.68:8000}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Env file not found: $ENV_FILE" >&2
  exit 1
fi

set_or_replace() {
  local key="$1"
  local value="$2"
  if grep -q "^${key}=" "$ENV_FILE"; then
    sed -i "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
  else
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
}

set_or_replace JWT_ALGORITHM RS256
set_or_replace JWT_PUBLIC_KEY_PATH /app/certs/public.pem
set_or_replace OPERATIONAL_GATEWAY_BASE_URL "$SECURITY_GATEWAY_URL"
set_or_replace OPERATIONAL_VEHICLES_PATH /vehiculos/
set_or_replace OPERATIONAL_ASSIGNMENTS_PATH /asignaciones/
set_or_replace OPERATIONAL_INCIDENTS_PATH /api/incidents/
set_or_replace OPERATIONAL_MAINTENANCE_PATH /api/v1/mantenimientos/

if [[ -n "${OPERATIONAL_GATEWAY_BEARER_TOKEN:-}" ]]; then
  set_or_replace OPERATIONAL_GATEWAY_BEARER_TOKEN "$OPERATIONAL_GATEWAY_BEARER_TOKEN"
fi

if [[ -n "${OPERATIONAL_GATEWAY_SERVICE_EMAIL:-}" ]]; then
  set_or_replace OPERATIONAL_GATEWAY_SERVICE_EMAIL "$OPERATIONAL_GATEWAY_SERVICE_EMAIL"
fi

if [[ -n "${OPERATIONAL_GATEWAY_SERVICE_PASSWORD:-}" ]]; then
  set_or_replace OPERATIONAL_GATEWAY_SERVICE_PASSWORD "$OPERATIONAL_GATEWAY_SERVICE_PASSWORD"
fi

sed -i '/^JWT_SECRET_KEY=/d' "$ENV_FILE"

echo "Security integration variables applied to $ENV_FILE"
