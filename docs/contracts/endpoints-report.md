## Veredicto: tokens y seguridad

El modelo de **Reports está bien planteado en diseño**, pero **no funciona de punta a punta en el despliegue actual** sin cambios operativos y de integración con Security.

### Dos flujos JWT distintos (correcto en concepto)

| Flujo | Quién | Token | Validación |
|-------|--------|-------|------------|
| **Entrada** (cliente → Reports) | Usuario vía Gateway o directo | JWT del usuario (`Authorization: Bearer`) | RS256 con `JWT_PUBLIC_KEY_PATH`; roles `ADMINISTRADOR` o `EMPLEADO_REPORTES` |
| **Salida** (Reports → Gateway → otros MS) | Reports como cliente HTTP | `OPERATIONAL_GATEWAY_BEARER_TOKEN` | Gateway valida JWT + RBAC; **no** se reenvía el token del usuario |

```65:95:c:\Users\lu\Downloads\code\2026-I\DSIII\ReportsService\backend\src\fleetops_reports\presentation\api\middleware.py
class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Any:
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)
        ...
        if str(payload.get("role", "")).upper() not in REPORTS_ALLOWED_ROLES:
            return JSONResponse(status_code=403, ...)
        request.state.jwt_payload = payload
        return await call_next(request)
```

```86:119:c:\Users\lu\Downloads\code\2026-I\DSIII\ReportsService\backend\src\fleetops_reports\composition\wiring.py
    gateway_url = settings.operational_gateway_base_url
    gateway_token = settings.operational_gateway_bearer_token
    ...
    vehicles_client=RestVehiclesClient(..., gateway_token, resource_path=settings.operational_vehicles_path),
```

### Qué funciona hoy

1. **Validación inbound RS256** en Reports (si `certs/public.pem` coincide con la clave de Security).
2. **Rutas alias de Reports** alineadas con convención Gateway: `/api/reports`, `/reports`.
3. **Rol `EMPLEADO_REPORTES`** aceptado dentro de Reports.

### Qué está roto o incompleto

| Problema | Impacto |
|----------|---------|
| `OPERATIONAL_GATEWAY_BEARER_TOKEN` vacío en EC2 | **401** al llamar `/api/vehicles/`, etc. |
| Token de servicio manual (~60 min) | Se cae la generación cuando expira; no hay renovación automática en Reports |
| Gateway **no reescribe rutas** — reenvía `{upstream}{path}` tal cual | Prefijos `/api/*` del Gateway **no coinciden** con rutas internas de varios MS → **404** aunque el token sea válido |
| `EMPLEADO_REPORTES` no está en el enum del Gateway | Usuario con ese rol puede entrar a Reports directo, pero **Security puede bloquearlo** en `/api/reports` |
| Rutas upstream solo permiten `ADMINISTRADOR` para reportes en Gateway | Falta registrar `EMPLEADO_REPORTES` en Security |
| Contratos JSON incidents/maintenance | Campos en español en Reports vs inglés en servicios desplegados |

El Gateway reenvía la ruta completa sin transformación:

```122:125:c:\Users\lu\Downloads\code\2026-I\DSIII\FleetOps-Security-Service\api_gateway\app\routes\proxy_routes.py
    upstream_base = _resolve_upstream_url(decision.route_entry.upstream_url_key)
    target_url = f"{upstream_base}{path}"
```

---

## Rutas después de `/api/`: ¿están correctas?

Hay **tres capas** que deben alinearse:

1. **Prefijo en Security** (`VEHICLES_SERVICE_PREFIX`, etc.)
2. **Lo que Reports llama** (`OPERATIONAL_*_PATH`)
3. **Lo que el microservicio expone realmente**

### Tabla de alineación

| Servicio | Prefijo Gateway (documentado en Reports) | Ruta real del microservicio | ¿Coincide vía Gateway? | Lo que Reports usa en EC2 |
|----------|------------------------------------------|----------------------------|------------------------|---------------------------|
| **Vehicles** | `/vehiculos` | `/vehiculos` | **Sí** (when Security prefix matches) | `/vehiculos/` |
| **Assignments** | `/asignaciones` | `/asignaciones` | **Parcial** (list endpoint may be missing) | `/asignaciones/` |
| **Incidents** | `/api/incidents` | `/api/incidents/` | **Sí** | `/api/incidents/` |
| **Maintenance** | `/api/v1/mantenimientos` | `/api/v1/mantenimientos` | **Sí** | `/api/v1/mantenimientos/` |
| **Reports** | `/api/reports` | `/api/reports`, `/reports` | **Parcial** (Reports expone ambos prefijos; Security debe registrar el prefijo) | N/A |

**Defaults en código** de Reports (`settings.py`) usan rutas en español **sin** `/api/` (`/vehiculos/`, `/incidentes/`, etc.), que tampoco coinciden con Incidents (`/api/incidents/`) ni Maintenance (`/api/v1/mantenimientos/`).

**Conclusión de rutas:** Los paths `/api/*` en EC2 son correctos **solo respecto al Gateway**, pero el Gateway **no los traduce** a las rutas internas. Eso es un gap de **Security/infra**, no solo de Reports. Opciones:

- **A)** Prefijos del Gateway = rutas reales (`/vehiculos`, `/asignaciones`, `/api/incidents`, `/api/v1/mantenimientos`) y Reports ajusta `OPERATIONAL_*_PATH` igual.
- **B)** Gateway implementa strip/rewrite de prefijo (no existe hoy).
- **C)** Cada MS expone aliases bajo `/api/*` (cambio en otros equipos).

---

## Inventario de endpoints por microservicio

### 1. Security — API Gateway (`:8000`)

| Método | Ruta | Auth | Destino |
|--------|------|------|---------|
| GET | `/health` | Pública | Gateway |
| POST | `/auth/register` | Pública | Auth `POST /register` |
| POST | `/auth/login` | Pública | Auth `POST /login` |
| * | `/{prefijo}/*` | JWT + RBAC | Proxy al MS según registry |

Prefijos configurables (secrets CI): `VEHICLES_SERVICE_PREFIX`, `ASSIGNMENTS_SERVICE_PREFIX`, `INCIDENTS_SERVICE_PREFIX`, `MAINTENANCE_SERVICE_PREFIX`, `REPORTS_SERVICE_PREFIX`.

Roles permitidos (registry local):

| Prefijo | Roles |
|---------|-------|
| `/auth` | Público |
| `/roles` | `ADMINISTRADOR` |
| Vehicles | `EMPLEADO_MANTENIMIENTO`, `EMPLEADO_INCIDENTES`, `ADMINISTRADOR` |
| Assignments | `EMPLEADO`, `ADMINISTRADOR` |
| Incidents | `EMPLEADO_INCIDENTES`, `ADMINISTRADOR` |
| Maintenance | `EMPLEADO_MANTENIMIENTO`, `ADMINISTRADOR` |
| Reports | **`ADMINISTRADOR` solamente** |

---

### 2. Security — Auth Service (interno `:8001`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health |
| POST | `/register` | Registro de usuario |
| POST | `/login` | Login → JWT |

---

### 3. Security — Role Service (interno `:8002`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health |
| POST | `/roles/validate` | Validación RBAC (Gateway) |
| POST | `/roles/assign` | Asignar rol |
| DELETE | `/roles/remove` | Quitar rol |
| GET | `/roles/user/{user_id}` | Roles de un usuario |

---

### 4. Vehicles Service — base `/vehiculos`

**Operaciones (JWT en MS salvo actuator):**

| Método | Ruta |
|--------|------|
| POST | `/vehiculos` |
| PUT | `/vehiculos/{id}` |
| PUT | `/vehiculos/placa/{placa}` |
| DELETE | `/vehiculos/{id}` |
| DELETE | `/vehiculos/placa/{placa}` |
| GET | `/vehiculos` ← **Reports necesita este** |
| GET | `/vehiculos/inactivos` |
| GET | `/vehiculos/{id}` |
| GET | `/vehiculos/placa/{placa}` |
| POST | `/vehiculos/{id}/reactivar` |
| POST | `/vehiculos/placa/{placa}/reactivar` |
| PATCH | `/vehiculos/{id}/estado` |
| PATCH | `/vehiculos/placa/{placa}/estado` |
| GET | `/vehiculos/disponibles` |
| GET | `/vehiculos/disponibles/tipo/{nombreTipo}` |
| GET | `/vehiculos/disponibles/rango` |
| GET | `/vehiculos/reservados` |
| GET | `/vehiculos/mantenimiento` |
| GET | `/vehiculos/fueradeservicio` |
| GET | `/vehiculos/{id}/disponibilidad` |
| GET | `/vehiculos/placa/{placa}/disponibilidad` |
| GET | `/vehiculos/{id}/disponibilidad/rango` |
| GET | `/vehiculos/placa/{placa}/disponibilidad/rango` |
| GET | `/vehiculos/historial` |
| GET | `/vehiculos/{id}/historial` |
| GET | `/vehiculos/placa/{placa}/historial` |
| GET | `/vehiculos/reservas` |
| GET | `/vehiculos/reservas/pendientes` |
| GET | `/vehiculos/reservas/confirmadas` |
| GET | `/vehiculos/reservas/canceladas` |
| GET | `/vehiculos/reservas/fallidas` |
| GET | `/vehiculos/reservas/{reservaId}` |
| GET | `/vehiculos/reservas/placa/{numeroPlaca}` |
| GET | `/vehiculos/reservas/placa/{numeroPlaca}/estado/{estado}` |
| POST | `/vehiculos/reservas/{idReserva}/compensar` |
| POST | `/vehiculos/placa/{placa}/reservas/cancelar` |
| GET | `/vehiculos/sagas` |
| GET | `/vehiculos/sagas/iniciadas` |
| GET | `/vehiculos/sagas/en-progreso` |
| GET | `/vehiculos/sagas/completadas` |
| GET | `/vehiculos/sagas/fallidas` |
| GET | `/vehiculos/sagas/compensadas` |
| GET | `/vehiculos/sagas/placa/{numeroPlaca}` |
| GET | `/vehiculos/sagas/placa/{numeroPlaca}/estado/{estado}` |
| POST | `/vehiculos/tipos-vehiculo` |
| PUT | `/vehiculos/tipos-vehiculo/{id}` |
| DELETE | `/vehiculos/tipos-vehiculo/{id}` |
| GET | `/vehiculos/tipos-vehiculo` |
| GET | `/vehiculos/tipos-vehiculo/{id}` |

**Públicos (actuator):** `/actuator/health`, `/actuator/info`, `/actuator/prometheus`, `/actuator/metrics`

---

### 5. Assignments Service — base `/asignaciones`

| Método | Ruta | Notas |
|--------|------|-------|
| POST | `/asignaciones` | Crear asignación |
| GET | `/asignaciones/saga/{idSaga}` | Consulta saga |
| — | **No existe `GET /asignaciones`** | Reports hace listado → fallará |

**Públicos:** `/actuator/**`, Swagger

---

### 6. Incidents Service

| Método | Ruta | Auth |
|--------|------|------|
| GET | `/health` | Pública |
| GET | `/api/incidents/` | JWT ← **Reports usa este** |
| POST | `/api/incidents/create/` | JWT |
| GET | `/api/incidents/{incident_id}/` | JWT |
| GET | `/api/schema/` | Docs |
| GET | `/api/swagger/` | Docs |
| GET | `/api/redoc/` | Docs |

---

### 7. Maintenance Service

| Método | Ruta | Auth |
|--------|------|------|
| GET | `/health` | Pública |
| GET | `/metrics` | Prometheus (si habilitado) |
| GET | `/api/v1/mantenimientos/` | JWT ← **Reports debería apuntar aquí** |
| GET | `/api/v1/mantenimientos/cola` | JWT |
| GET | `/api/v1/mantenimientos/reporte` | JWT |
| GET | `/api/v1/mantenimientos/{id}` | JWT |

---

### 8. Reports Service

**Públicos:** `/health`, `/metrics`, `/docs`, `/openapi.json`, `/redoc`

**Protegidos** (mismos handlers en 2 prefijos):

| Método | Ruta (×2 prefijos) |
|--------|---------------------|
| POST | `{prefix}/generate` |
| GET | `{prefix}` |
| GET | `{prefix}/{report_id}` |
| GET | `{prefix}/{report_id}/download` |

Prefijos: `/reports`, `/api/reports`

---

## Cambios necesarios (priorizados)

### Inmediato (ops, sin código)

1. Poblar `OPERATIONAL_GATEWAY_BEARER_TOKEN` con JWT de **`ADMINISTRADOR`** (no sirve el del usuario `EMPLEADO_REPORTES` para upstream).
2. Security: registrar `REPORTS_SERVICE_URL`, `REPORTS_SERVICE_PREFIX=/api/reports`, rol `EMPLEADO_REPORTES` en ruta de reportes.

### Security / infra (otros equipos)

3. Alinear prefijos Gateway con rutas reales **o** implementar rewrite.
4. Ejemplo coherente si no hay rewrite:

```env
VEHICLES_SERVICE_PREFIX=/vehiculos
ASSIGNMENTS_SERVICE_PREFIX=/asignaciones
INCIDENTS_SERVICE_PREFIX=/api/incidents
MAINTENANCE_SERVICE_PREFIX=/api/v1/mantenimientos
REPORTS_SERVICE_PREFIX=/api/reports
```

Y en Reports EC2 los mismos valores en `OPERATIONAL_*_PATH`.

### En Reports (código — cuando pases a Agent mode)

5. Renovación automática del token de servicio (`POST /auth/login`).
6. Mapeo de campos incidents/maintenance al contrato desplegado.
7. Tolerar ausencia de `GET /asignaciones`.
8. Paginación Spring en Vehicles (`content`, `totalPages`).
9. Filtro por `ciudad_operacion` si lo necesitas.

---

## Respuesta directa a tu pregunta

**¿Funciona el sistema actual de tokens y validaciones?**

- **Entrada a Reports:** Sí, en diseño; falta que Security exponga `/api/reports` y permita `EMPLEADO_REPORTES`.
- **Salida Reports → Gateway → otros MS:** **No funciona hoy** (token vacío + desalineación de rutas + contratos JSON + sin listado de asignaciones).
- **Rutas `/api/*` en Reports EC2:** Correctas **hacia el Gateway**, pero **incorrectas hacia los microservicios** mientras el Gateway no reescriba paths.

Si quieres, en Agent mode puedo proponer el diff concreto en Reports (paths, mapeos, renovación de token y filtro por ciudad) una vez Security confirme los prefijos finales del Gateway.