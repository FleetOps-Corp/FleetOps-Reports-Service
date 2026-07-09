#!/usr/bin/env bash
# Install and configure Grafana Alloy on the Reports EC2 host.
# Credentials are read from /etc/alloy/credentials.env (never commit secrets).
set -euo pipefail

CREDENTIALS_FILE="${ALLOY_CREDENTIALS_FILE:-/etc/alloy/credentials.env}"
CONFIG_FILE="/etc/alloy/config.alloy"
REPO_ROOT="${REPO_ROOT:-/opt/fleetops-reports}"
EXAMPLE_CONFIG="${REPO_ROOT}/observability/alloy.config.alloy.example"

require_root() {
  if [[ "${EUID}" -ne 0 ]]; then
    echo "Run as root (sudo)." >&2
    exit 1
  fi
}

install_alloy() {
  if command -v alloy >/dev/null 2>&1; then
    echo "Alloy already installed: $(alloy --version 2>/dev/null || true)"
    return
  fi

  if [[ ! -f "${CREDENTIALS_FILE}" ]]; then
    echo "Missing ${CREDENTIALS_FILE}. Create it before installing Alloy." >&2
    exit 1
  fi

  # shellcheck disable=SC1090
  set -a
  source "${CREDENTIALS_FILE}"
  set +a

  : "${GCLOUD_RW_API_KEY:?GCLOUD_RW_API_KEY is required in credentials file}"
  : "${GCLOUD_HOSTED_METRICS_URL:?GCLOUD_HOSTED_METRICS_URL is required}"
  : "${GCLOUD_HOSTED_METRICS_ID:?GCLOUD_HOSTED_METRICS_ID is required}"

  ARCH="${ARCH:-amd64}"
  GCLOUD_SCRAPE_INTERVAL="${GCLOUD_SCRAPE_INTERVAL:-60s}"
  export ARCH GCLOUD_HOSTED_METRICS_URL GCLOUD_HOSTED_METRICS_ID GCLOUD_RW_API_KEY
  export GCLOUD_HOSTED_LOGS_URL GCLOUD_HOSTED_LOGS_ID GCLOUD_SCRAPE_INTERVAL

  /bin/sh -c "$(curl -fsSL https://storage.googleapis.com/cloud-onboarding/alloy/scripts/install-linux.sh)"
}

write_config() {
  if [[ ! -f "${EXAMPLE_CONFIG}" ]]; then
    echo "Missing ${EXAMPLE_CONFIG}" >&2
    exit 1
  fi
  install -d -m 0750 /etc/alloy
  cp "${EXAMPLE_CONFIG}" "${CONFIG_FILE}"
  chmod 0640 "${CONFIG_FILE}"
}

write_systemd_override() {
  install -d -m 0755 /etc/systemd/system/alloy.service.d
  cat >/etc/systemd/system/alloy.service.d/override.conf <<EOF
[Service]
EnvironmentFile=${CREDENTIALS_FILE}
EOF
}

restart_alloy() {
  systemctl daemon-reload
  systemctl enable alloy.service
  systemctl restart alloy.service
  systemctl --no-pager --full status alloy.service
}

verify_metrics() {
  local target="${REPORTS_METRICS_TARGET:-127.0.0.1:8081}"
  echo "Checking local metrics at http://${target}/metrics"
  curl -fsS "http://${target}/metrics" | head -n 20
}

main() {
  require_root
  install_alloy
  write_config
  write_systemd_override
  restart_alloy
  verify_metrics
  echo "Alloy configured. Metrics remote_write -> Grafana Cloud Prometheus."
}

main "$@"
