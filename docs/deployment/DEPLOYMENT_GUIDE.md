# FleetOps Reports — Production Deployment Guide (EC2 Free Tier)

This guide walks through deploying FleetOps Reports on a single **AWS EC2 free-tier** instance using Docker Compose, MongoDB Atlas M0, co-located MinIO, and integration with the external **FleetOps Security Gateway**.

All secret values must be generated and stored outside version control. This document uses placeholders only.

---

## 1. Architecture Overview

```
                    Internet
                        │
                        ▼
              ┌─────────────────┐
              │  EC2 Instance   │
              │  (free tier)    │
              │                 │
              │  ┌───────────┐  │         ┌──────────────────────┐
              │  │  gateway  │◄─┼─ :8081 ─┤  Clients / testers   │
              │  │  (nginx)  │  │         └──────────────────────┘
              │  └─────┬─────┘  │
              │        │        │
              │  ┌─────▼─────┐  │
              │  │  backend  │──┼──► MongoDB Atlas M0 (free tier)
              │  └─────┬─────┘  │
              │        │        │
              │  ┌─────▼─────┐  │
              │  │   minio   │  │  PDFs + graph objects
              │  └───────────┘  │
              └────────┬────────┘
                       │ HTTPS/HTTP + JWT
                       ▼
              ┌─────────────────┐
              │ FleetOps        │
              │ Security Gateway│──► vehicles / assignments /
              │ (external)      │    incidents / maintenance
              └─────────────────┘
```

**Default production stack:** gateway + backend + MinIO on EC2. MongoDB on Atlas. Observability disabled to preserve free-tier resources.

---

## 2. Prerequisites

### 2.1 Accounts and access

- AWS account with EC2 free tier eligibility
- GitHub repository access (FleetOps Reports)
- MongoDB Atlas account (M0 cluster)
- FleetOps Security Gateway reachable from the EC2 public IP
- ADMINISTRADOR credentials for the Security Gateway

### 2.2 Local tools (operator workstation)

- SSH client
- Git
- Optional: AWS CLI for instance management

---

## 3. MongoDB Atlas M0 (Recommended)

Using Atlas avoids running MongoDB on a memory-constrained EC2 instance.

1. Create a **M0 free cluster** in MongoDB Atlas.
2. Create a database user with read/write access to the reports database.
3. Add the EC2 public IP to the Atlas **IP Access List** (or `0.0.0.0/0` temporarily for initial setup — tighten afterwards).
4. Copy the **SRV connection string** from Atlas.
5. Replace placeholders in the connection string:

```
mongodb+srv://<db_username>:<db_password>@<cluster-host>/<database_name>?retryWrites=true&w=majority
```

6. Set `MONGODB_DATABASE` to match the database name in the URI.

> **Do not** enable the `embedded-db` Compose profile when using Atlas.

---

## 4. Provision the EC2 Instance

### 4.1 Instance specification (free tier)

| Setting | Recommendation |
|---------|----------------|
| AMI | Ubuntu 22.04 LTS |
| Instance type | `t2.micro` or `t3.micro` |
| Storage | 20–30 GiB gp3 |
| Key pair | Create or reuse an SSH key pair |

### 4.2 Security group inbound rules

| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 22 | TCP | Your IP / team CIDR | SSH administration |
| 8081 | TCP | Required clients | Reports API gateway |
| 3000 | TCP | Optional, restricted | Grafana (only if observability profile enabled) |

Do **not** expose MinIO ports (9000/9001) to the public internet in production.

### 4.3 Install Docker on the instance

Connect via SSH and install Docker Engine and the Compose plugin:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker "$USER"
```

Log out and back in so group membership applies.

Verify:

```bash
docker --version
docker compose version
```

---

## 5. One-Time Host Setup

### 5.1 Clone the repository

```bash
sudo mkdir -p /opt/fleetops-reports
sudo chown "$USER":"$USER" /opt/fleetops-reports
git clone <repository-url> /opt/fleetops-reports
cd /opt/fleetops-reports
git checkout main
```

### 5.2 Create the production environment file

```bash
cp .env.production.example .env
chmod 600 .env
```

Edit `.env` and set every placeholder:

| Variable | Guidance |
|----------|----------|
| `GATEWAY_HTTP_PORT` | `8081` (matches security group) |
| `APP_ENVIRONMENT` | `production` |
| `MONGODB_URI` | Atlas SRV string from Section 3 |
| `MONGODB_DATABASE` | Database name (e.g. `fleetops_reports`) |
| `MINIO_ACCESS_KEY` | Random string (≥ 16 characters) |
| `MINIO_SECRET_KEY` | Random string (≥ 32 characters) |
| `OPERATIONAL_GATEWAY_BASE_URL` | Security Gateway base URL |
| `OPERATIONAL_GATEWAY_BEARER_TOKEN` | JWT from Section 6 |
| `LOG_LEVEL` | `INFO` or `WARNING` in production |

Generate random secrets locally:

```bash
openssl rand -hex 16   # example for access keys
openssl rand -hex 32   # example for secret keys
```

### 5.3 Obtain the Security Gateway JWT

From any machine that can reach the Security Gateway:

```bash
curl -s -X POST "<SECURITY_GATEWAY_URL>/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"<admin_email>","password":"<admin_password>"}'
```

Copy the token from the response and set `OPERATIONAL_GATEWAY_BEARER_TOKEN` in `.env`.

> Tokens expire (default: 60 minutes in Security Service). For production, implement token refresh or a service account strategy with the Security team.

---

## 6. Start the Application Stack

### 6.1 Default production start (recommended)

```bash
cd /opt/fleetops-reports
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
```

### 6.2 Optional profiles

**Embedded MongoDB** (not recommended on free-tier EC2 if Atlas is available):

```bash
docker compose -f docker-compose.prod.yml --profile embedded-db --env-file .env up -d --build
```

**Observability** (Prometheus, Grafana, Loki, Promtail — requires additional RAM):

```bash
docker compose -f docker-compose.prod.yml --profile observability --env-file .env up -d --build
```

### 6.3 Verify health

```bash
docker compose -f docker-compose.prod.yml --env-file .env ps
curl -f "http://127.0.0.1:8081/health"
```

Expected: HTTP 200 from the health endpoint.

### 6.4 Smoke test report generation

```bash
curl -s -X POST "http://<EC2_PUBLIC_IP>:8081/reports/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "report_id": "rep-smoke-001",
    "title": "Smoke Test Report",
    "start_date": "2026-05-01",
    "end_date": "2026-05-31"
  }'
```

This call succeeds only when:

1. MongoDB Atlas is reachable from EC2.
2. MinIO is healthy.
3. The Security Gateway accepts the JWT.
4. Upstream operational microservices respond through the gateway.

---

## 7. Enable Automated Deployment (GitHub Actions)

Complete Section 5 first. Then configure GitHub:

### 7.1 Repository secrets

Navigate to **Settings → Secrets and variables → Actions** and create:

| Secret | Value |
|--------|-------|
| `EC2_HOST` | EC2 public IP or DNS |
| `EC2_USER` | SSH username |
| `EC2_SSH_KEY` | Full private key PEM contents |
| `DEPLOY_PATH` | `/opt/fleetops-reports` (optional) |

### 7.2 Enable the deploy workflow

In `.github/workflows/deploy.yml`, replace `if: false` with the activation condition documented in [DEPLOYMENT_CONFIGURATION.md](./DEPLOYMENT_CONFIGURATION.md).

### 7.3 Trigger deployment

- **Automatic:** merge to `main` after CI succeeds.
- **Manual:** Actions → *FleetOps Reports Deployment* → *Run workflow*.

The workflow will SSH into EC2, pull the latest code, rebuild containers, and verify `/health`.

---

## 8. Operations

### 8.1 View logs

```bash
docker compose -f docker-compose.prod.yml --env-file .env logs -f backend
docker compose -f docker-compose.prod.yml --env-file .env logs -f gateway
```

### 8.2 Restart after configuration changes

```bash
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
```

### 8.3 Stop the stack

```bash
docker compose -f docker-compose.prod.yml --env-file .env down
```

Data persists in named volumes (`minio_data`, `backend_logs`, and optionally `mongodb_data`, `loki_data`).

### 8.4 Update the Security Gateway token

When the JWT expires, update `.env` on the host and restart the backend:

```bash
docker compose -f docker-compose.prod.yml --env-file .env up -d backend
```

---

## 9. Free-Tier Resource Guidance

| Component | Free-tier strategy |
|-----------|-------------------|
| EC2 | Single `t2.micro` / `t3.micro`; monitor memory with `free -h` |
| MongoDB | Atlas M0 (512 MB) — do not run `embedded-db` profile |
| MinIO | Co-located; buckets created automatically on first upload |
| Observability | Disable unless instance has headroom; profile is optional |
| Security Gateway | External; ensure Security team opens access from EC2 IP |

If the instance becomes memory-starved:

1. Confirm observability profile is **not** running.
2. Confirm MongoDB is on Atlas, not embedded.
3. Reduce Docker log retention or restart periodically during demos.

---

## 10. Troubleshooting

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| `/health` fails | Backend not started | Check `docker compose ps` and backend logs |
| Report returns 503/422 | Gateway token missing or expired | Refresh `OPERATIONAL_GATEWAY_BEARER_TOKEN` |
| Report fails on data fetch | Operational services down | Verify Security Gateway routes with JWT |
| MongoDB connection error | Atlas IP not allowlisted | Add EC2 public IP to Atlas access list |
| MinIO upload error | Invalid credentials | Verify `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` |
| Deploy workflow never runs | `if: false` still set | Enable condition per configuration doc |
| Deploy workflow fails SSH | Missing or wrong secrets | Verify `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY` |

---

## 11. Security Checklist

- [ ] `.env` file permissions set to `600`
- [ ] No secrets committed to Git
- [ ] MinIO ports not exposed publicly
- [ ] SSH restricted to trusted IP ranges
- [ ] Atlas IP access list scoped to EC2
- [ ] JWT rotated on schedule
- [ ] Security group reviewed before demo/production use

---

## 12. Related Documentation

- [DEPLOYMENT_CONFIGURATION.md](./DEPLOYMENT_CONFIGURATION.md) — CI/CD and artifact reference
- [.env.production.example](../../.env.production.example) — Variable template
- [README.md](../../README.md) — Developer setup and validation commands
