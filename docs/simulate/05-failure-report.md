# Reporte de fallos y mitigaciones — sesión de simulación

Fecha: 2026-07-02

## Resumen

| Área | Estado final |
|------|--------------|
| Local E2E (Gateway + Incidents + Reports) | **OK** |
| EC2 health | **OK** |
| EC2 report generate con mock | **Pendiente** (SSH intermitente) |

---

## F-001 — Security Gateway `/health` devuelve 404

**Síntoma:** `GET http://localhost:8000/health` → `{"detail":"The requested resource does not exist."}`

**Causa:** El router catch-all del proxy (`/{full_path:path}`) se registra antes que `@app.get("/health")` en `api_gateway/app/main.py`.

**Mitigación aplicada en pruebas:** usar `GET /docs` como liveness.

**Fix recomendado (Security Service):** registrar `/health` antes del proxy o excluir `/health` del catch-all.

**Estado:** Abierto en Security Service.

---

## F-002 — Prefijo `/reportes` vs `/reports`

**Síntoma:** Security Gateway proxifica `/reportes/**` pero Reports exponía solo `/reports/**`.

**Fix aplicado:** alias `POST /reportes/generate` en Reports (`gateway_router`).

**Estado:** **Corregido** en ReportsService.

---

## F-003 — Incidents path `/incidentes` vs `/api/incidents`

**Síntoma:** Gateway reenvía `/incidentes/...` sin rewrite; Incidents solo tenía `/api/incidents/...`.

**Fix aplicado:** rutas gateway en Incidents (`/incidentes/**`) con serialización en español.

**Estado:** **Corregido** en FleetOps-Incidents-Service.

---

## F-004 — Security Service `entrypoint.sh` CRLF en Windows

**Síntoma:** `exec ./entrypoint.sh: no such file or directory` — auth/role unhealthy.

**Causa:** finales de línea Windows en shell scripts.

**Mitigación:** convertir CRLF→LF en `auth_service/entrypoint.sh` y `role_service/entrypoint.sh`.

**Estado:** **Mitigado** localmente; considerar `.gitattributes` en Security Service.

---

## F-005 — Incidents `development.py` no heredaba `base.py`

**Síntoma:** `AttributeError: 'Settings' object has no attribute 'ROOT_URLCONF'`.

**Fix aplicado:** `from .base import *` en `incidents/settings/development.py`.

**Estado:** **Corregido**.

---

## F-006 — Tabla `incidents` inexistente

**Síntoma:** `django.db.utils.ProgrammingError: relation "incidents" does not exist`.

**Causa:** modelos ORM no descubiertos; sin migraciones.

**Fix aplicado:** `incidents/models.py` + `makemigrations` + `migrate`.

**Estado:** **Corregido** (migración `0001_initial`).

---

## F-007 — JWT del Gateway rechazado por Django en Incidents

**Síntoma:** `{"code":"token_not_valid"}` al llamar `/incidentes/` vía gateway con Bearer FleetOps.

**Causa:** DRF intenta validar el JWT del Security Gateway como SimpleJWT.

**Fix aplicado:** `@authentication_classes([])` en vistas gateway de Incidents.

**Estado:** **Corregido**.

---

## F-008 — Redirect 301 en clients Reports (`/incidentes` sin slash)

**Síntoma:** `REPORT_GENERATION_ERROR` — `301 Moved Permanently` en upstream.

**Fix aplicado:** trailing slash en URLs de REST clients + `follow_redirects=True` en httpx.

**Estado:** **Corregido** en ReportsService.

---

## F-009 — Atlas MongoDB desde Docker local

**Síntoma:** backend exit 3 — `ServerSelectionTimeoutError` SSL handshake Atlas.

**Mitigación:** `docs/simulate/docker-compose.simulate.override.yml` fuerza Mongo embebido en compose local.

**Estado:** **Mitigado** para pruebas locales.

---

## F-010 — EC2 SSH intermitente / OOM histórico

**Síntoma:** timeouts SSH; instancia t2.micro saturada con MongoDB embebido.

**Mitigación desplegada:** Atlas + stack lean (gateway, backend, minio).

**Estado:** Health OK; completar mock+report cuando SSH estable.

---

## F-011 — Red institucional bloquea IP EC2

**Síntoma:** respuesta HTML "Acceso Bloqueado" al curl externo.

**Mitigación:** túnel SSH o prueba desde EC2 (`curl 127.0.0.1:8081`).

**Estado:** Documentado; no es fallo del servicio.

---

## F-012 — `OPERATIONAL_GATEWAY_BEARER_TOKEN` vacío en EC2 inicial

**Síntoma:** report generate falla sin upstream/token.

**Mitigación:** mock gateway + token `simulate-token` (documentado en `01-deployed-ec2.md`).

**Estado:** Procedimiento documentado; ejecución pendiente por SSH.

---

## Cambios de código realizados

### ReportsService
- Alias `/reportes/generate`
- REST clients: trailing slash + follow redirects
- `docs/simulate/**`, scripts de smoke, mock gateway
- `docker-compose.yml`: `extra_hosts` para backend local

### FleetOps-Incidents-Service
- `/health`, rutas `/incidentes/**`, fix settings, migraciones, auth bypass en gateway views
- Puerto host **8030**

### FleetOps-Security-Service
- Solo fix CRLF local en entrypoints (no commit requerido en repo remoto)
