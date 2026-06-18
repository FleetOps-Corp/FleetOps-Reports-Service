# Correcciones Realizadas — FleetOps Reports Archetype

**Fecha:** 2026-06-17  
**Contexto:** Continuación de la generación del arquetipo tras la revisión contra el SAD y el prompt original. Codex generó ~190 archivos pero se detuvo antes de validar el despliegue completo y el cumplimiento de cobertura al 100%.

---

## Resumen ejecutivo

Se identificaron **7 brechas reales** en el arquetipo generado. El resto del blueprint (ADR-004, Loki/Promtail, API Gateway, protos sin versionar, excepciones de dominio, mappers, DI, presigned URLs, conftest, Makefile) ya estaba correctamente implementado.

Tras las correcciones, el stack levanta con `docker compose up --build`, el flujo `POST /reports` funciona end-to-end, **35 tests pasan** y la cobertura de `domain` + `application` alcanza **100%**.

---

## Correcciones aplicadas

### 1. Observabilidad Loki — recolección de logs sin Docker socket

| Archivo | Cambio |
|---------|--------|
| `backend/src/fleetops_reports/config/settings.py` | Nuevo campo `LOG_FILE_PATH` |
| `backend/src/fleetops_reports/infrastructure/observability/logging.py` | Logging JSON a stdout **y** archivo opcional |
| `backend/src/fleetops_reports/main.py` | Pasa `log_file_path` a `configure_logging()` |
| `.env.example` | Variable `LOG_FILE_PATH=/var/log/fleetops-reports/app.log` |
| `backend/Dockerfile` | Crea `/var/log/fleetops-reports` con permisos para usuario `app` |
| `docker-compose.yml` | Volumen compartido `backend_logs` entre backend y promtail |
| `observability/promtail-config.yml` | Scraping por archivo (`/var/log/fleetops-reports/*.log`) en lugar de `docker_sd_configs` |

**Motivo:** Promtail con acceso al socket de Docker contradice el hard constraint non-root y no es portable. El SAD exige Loki; la recolección por volumen compartido es la alternativa alineada al arquetipo.

---

### 2. Contenedores non-root explícitos

| Archivo | Cambio |
|---------|--------|
| `docker-compose.yml` | `user:` explícito en gateway (101), backend (10001), mongodb (999), minio (10001), prometheus (65534), grafana (472), loki (10001), promtail (10001) |
| `gateway/Dockerfile` | Comentario explícito: `nginxinc/nginx-unprivileged`, non-root runtime |

---

### 3. MinIO non-root con imagen local

| Archivo | Cambio |
|---------|--------|
| `minio/Dockerfile` | **Nuevo.** Wrapper sobre imagen oficial pineada; crea `/data` y asigna `USER 10001:10001` |
| `docker-compose.yml` | MinIO pasa de `image:` a `build: ./minio` |

**Motivo:** La imagen oficial de MinIO corre como root; con `user:` forzado en compose fallaba con `file access denied` en el volumen.

---

### 4. Variables de entorno del backend en compose

| Archivo | Cambio |
|---------|--------|
| `docker-compose.yml` | Backend carga `.env.example` como base y `.env` como override opcional |

**Motivo:** Sin `.env` local, el backend arrancaba con `ValidationError` por settings faltantes.

---

### 5. Beanie 2.x — cliente MongoDB async compatible

| Archivo | Cambio |
|---------|--------|
| `backend/pyproject.toml` | Eliminada dependencia directa `motor==3.7.1` (Beanie 2.x usa PyMongo async) |
| `backend/src/fleetops_reports/infrastructure/persistence/mongodb/mongo_client.py` | `AsyncIOMotorClient` → `pymongo.AsyncMongoClient` |

**Motivo:** Error en runtime: `MotorDatabase object is not callable` al inicializar Beanie 2.1.0.

---

### 6. Fixtures unitarias funcionales

| Archivo | Cambio |
|---------|--------|
| `backend/tests/unit/conftest.py` | Fixtures `unit_report_service` y `unit_generate_report_use_case` (antes solo docstring) |

---

### 7. Cobertura 100% en domain + application

| Archivo | Cambio |
|---------|--------|
| `backend/tests/unit/domain/test_exceptions.py` | **Nuevo.** Cubre `DomainError.to_dict()` |
| `backend/tests/unit/domain/test_availability_policy.py` | Caso vehículo operacional (rama positiva) |
| `backend/tests/unit/application/test_generate_report.py` | Casos: re-raise `DomainError` y wrap de errores inesperados |

**Resultado:** 328 statements, 0 miss, **100% coverage** con `fail_under = 100`.

---

## Validaciones ejecutadas post-corrección

| Validación | Resultado |
|------------|-----------|
| `docker compose --env-file .env.example config` | ✅ Sintaxis válida |
| `docker build ./backend` | ✅ Python 3.12.13, protos generados en build |
| `docker compose up --build` | ✅ 8 servicios healthy/running |
| `GET http://localhost:8080/health` (via gateway) | ✅ `{"status":"ok"}` |
| `POST http://localhost:8080/reports` | ✅ Reporte generado con 3 KPIs y PDF en MinIO |
| `pytest` (Docker Python 3.12) | ✅ 35 passed |
| `coverage report` | ✅ 100% domain + application |

---

## Elementos verificados sin corrección

- ADR-004 documentado en README
- No hay stubs `*_pb2.py` versionados; `generated/` en `.gitignore`
- API Gateway con `nginxinc/nginx-unprivileged:1.27.5-alpine`
- Presigned URLs en `presigned_url_service.py` integradas en flujo WeasyPrint
- `domain/exceptions.py` completamente definido
- `dependencies.py`, `report_mapper.py`, tres `conftest.py` presentes
- Imágenes Docker pineadas (sin tags `latest`)

---

## Limitaciones conocidas (sin cambio en esta etapa)

1. **Violaciones de capas estrictas:** `presentation` importa `infrastructure` (DI, metrics); `infrastructure/mappers` importa `presentation/schemas`. Documentado en el reporte de validación arquitectónica.
2. **Clientes gRPC:** datos determinísticos locales; stubs reales pendientes de servicios FleetOps.
3. **Grafana:** dashboard JSON presente; provisioning automático de datasource no incluido.

---

## Próxima etapa

Revisión arquitectónica automatizada completada — ver [`REPORTE_VALIDACION_ARQUITECTURA.md`](REPORTE_VALIDACION_ARQUITECTURA.md).

### Correcciones adicionales (etapa de revisión 2026-06-18)

| Archivo | Cambio |
|---------|--------|
| `backend/src/fleetops_reports/domain/__init__.py` | Paquete domain reconocible por Import Linter |
| `backend/.importlinter` | 5 contratos arquitectónicos |
| `backend/mypy.ini`, `backend/pyproject.toml` | MyPy + Ruff + deps lint |
| `backend/scripts/run_validation_report.sh` | Script validación completa |
| `Makefile` | Targets lint/validate |
| Varios | Fixes MyPy (jinja, weasyprint), Ruff exclude generated/ |
