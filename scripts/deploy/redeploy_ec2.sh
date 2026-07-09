#!/usr/bin/env bash
# Safe EC2 redeploy: rebuild only backend, keep MinIO data, verify health.
set -euo pipefail

TARGET_DIR="${1:-/opt/fleetops-reports}"
cd "${TARGET_DIR}"

if [ ! -f .env ]; then
  echo "Missing .env in ${TARGET_DIR}" >&2
  exit 1
fi

BRANCH="${DEPLOY_BRANCH:-aquiceno}"
echo "Pulling ${BRANCH}..."
git fetch origin "${BRANCH}"
git checkout "${BRANCH}"
git pull --ff-only origin "${BRANCH}" || {
  git stash push -u -m "deploy-stash-$(date +%s)" || true
  git pull --ff-only origin "${BRANCH}"
}

echo "Rebuilding backend only (avoids heavy full-stack rebuild on small instances)..."
docker compose -f docker-compose.prod.yml --env-file .env up -d --build --no-deps backend

echo "Waiting for backend health..."
for _ in $(seq 1 30); do
  if docker compose -f docker-compose.prod.yml --env-file .env exec -T backend \
    python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health').read()" \
    >/dev/null 2>&1; then
    break
  fi
  sleep 5
done

docker compose -f docker-compose.prod.yml --env-file .env up -d gateway

GATEWAY_PORT="$(grep -E '^GATEWAY_HTTP_PORT=' .env | cut -d= -f2- | tr -d '\r' || true)"
GATEWAY_PORT="${GATEWAY_PORT:-8081}"
curl --fail --silent --show-error "http://127.0.0.1:${GATEWAY_PORT}/health"
echo
docker compose -f docker-compose.prod.yml --env-file .env ps
