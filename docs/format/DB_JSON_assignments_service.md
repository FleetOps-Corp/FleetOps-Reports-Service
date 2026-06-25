Aquí tienes la especificación técnica de las tablas del módulo de **Asignaciones y Conductores**, estructuradas según las migraciones Flyway reales del proyecto FleetOps Asignaciones.

---

## 1. Base de Datos

### Tabla: `conductores` (Maestro de Conductores)
> **Migración:** `V1__create_conductores.sql`

| Columna | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `id` | `UUID` | PRIMARY KEY, DEFAULT gen_random_uuid() | Identificador único del conductor generado automáticamente. |
| `nombre` | `VARCHAR(200)` | NOT NULL | Nombre completo del operador del vehículo. |
| `tipo_vehiculo` | `VARCHAR(100)` | NOT NULL | Categoría de vehículo que el conductor está habilitado para operar (ej: `CAMION`). |
| `estado` | `VARCHAR(50)` | NOT NULL | Estado operativo del conductor. Valores válidos en dominio: `DISPONIBLE`, `RESERVADO`, `INACTIVO`. |

**Datos de ejemplo (seed):**

```sql
INSERT INTO conductores (id, nombre, tipo_vehiculo, estado) VALUES
  ('11111111-1111-1111-1111-111111111111', 'Juan Pérez',     'CAMION', 'DISPONIBLE'),
  ('22222222-2222-2222-2222-222222222222', 'María Gómez',    'CAMION', 'DISPONIBLE'),
  ('33333333-3333-3333-3333-333333333333', 'Carlos Sánchez', 'CAMION', 'DISPONIBLE');
```

---

### Tabla: `asignaciones` (Frontera Contractual / Agregado Operativo)
> **Migración:** `V2__create_asignaciones.sql`

| Columna | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `id` | `UUID` | PRIMARY KEY, DEFAULT gen_random_uuid() | Identificador único del contrato operativo de asignación. |
| `conductor_id` | `UUID` | NOT NULL, FK → `conductores(id)` | Conductor asignado al servicio. |
| `vehiculo_id` | `UUID` | NULL | ID del vehículo confirmado por FleetOps Vehículos. **Nullable** — se llena de forma asíncrona cuando Vehículos publica el evento de confirmación. |
| `tipo_vehiculo` | `VARCHAR(100)` | NOT NULL | Tipo de vehículo solicitado en la asignación (ej: `CAMION`). |
| `fecha_inicio` | `DATE` | NOT NULL | Fecha en la que inicia la vigencia de la asignación. |
| `fecha_fin` | `DATE` | NOT NULL | Fecha proyectada para la finalización de la asignación. |
| `creada_en` | `TIMESTAMP` | NOT NULL, DEFAULT NOW() | Fecha de creación de la orden de asignación. |

> **Nota de Diseño:** `vehiculo_id` es intencionalmente `NULL` al momento de la creación. La asignación se registra en estado pendiente mientras Vehículos procesa de forma autónoma la solicitud vía Kafka. Se completa cuando llega el evento `VehiculoConfirmadoEvent`.

---

### Tabla: `licencias` (Habilitaciones del Conductor)
> **Migración:** `V3__create_licencias.sql`

| Columna | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `id` | `UUID` | PRIMARY KEY, DEFAULT gen_random_uuid() | Identificador único del registro de licencia. |
| `conductor_id` | `UUID` | NOT NULL, FK → `conductores(id)` | Conductor al que pertenece la habilitación. |
| `categoria` | `VARCHAR(50)` | NOT NULL | Categoría de licencia otorgada (ej: `C1`, `C2`). |
| `fecha_vencimiento` | `DATE` | NOT NULL | Control de vigencia legal. La entidad `Licencia.java` expone el método `estaVigente()` que compara este valor contra la fecha actual. |

---

### Tabla: `saga_registros` (Trazabilidad SAGA Coreografiada)
> **Migración:** `V4__create_saga_registros.sql`

| Columna | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `id` | `UUID` | PRIMARY KEY, DEFAULT gen_random_uuid() | Identificador único del registro de trazabilidad SAGA. |
| `asignacion_id` | `UUID` | FK → `asignaciones(id)`, NULL | Llave foránea que conecta con la asignación que originó la saga. |
| `estado` | `VARCHAR(60)` | NOT NULL | Estado actual del proceso distribuido. Valores válidos en dominio: `PENDIENTE_VEHICULO`, `PENDIENTE_LIBERACION`, `COMPLETADO`, `FALLIDO`. |
| `vehiculo_id` | `UUID` | NULL | ID del vehículo confirmado. Se llena cuando la SAGA alcanza el estado `COMPLETADO`. |
| `motivo_fallo` | `TEXT` | NULL | Registro del motivo de rechazo o error cuando la SAGA alcanza el estado `FALLIDO`. |
| `creada_en` | `TIMESTAMP` | NOT NULL, DEFAULT NOW() | Fecha y hora de inicio de la transacción distribuida. |
| `actualizada_en` | `TIMESTAMP` | NOT NULL, DEFAULT NOW() | Último cambio de estado registrado en la saga. |

**Índice:**
```sql
CREATE INDEX idx_saga_asignacion ON saga_registros (asignacion_id);
```

> **Nota de Diseño:** Esta tabla **no contiene** columnas de outbox (`siguiente_accion`, `intentos`, `maximo_intentos`). El flujo avanza por reacción a eventos Kafka, no por polling. El producer Kafka está configurado como transaccional — si el commit de DB falla, el mensaje Kafka también se descarta automáticamente.

---

## 2. Formato de Identificadores

Todos los identificadores primarios son **UUID v4** generados automáticamente por PostgreSQL (`gen_random_uuid()`). No se usan identificadores alfanuméricos legibles ni secuenciales.

```
id (conductores)      → UUID  ej: 11111111-1111-1111-1111-111111111111
id (asignaciones)     → UUID  ej: 6ba7b810-9dad-11d1-80b4-00c04fd430c8
id (saga_registros)   → UUID  ej: 550e8400-e29b-41d4-a716-446655440000
id (licencias)        → UUID  ej: dc912c19-25d1-4d29-be08-0f03f2459f45
vehiculo_id           → UUID  ej: 11111111-1111-1111-1111-111211111111
```

---

## 3. Ejemplos de Representación JSON (Payloads de API)

### JSON: `conductores`

```json
{
  "id": "11111111-1111-1111-1111-111111111111",
  "nombre": "Juan Pérez",
  "tipo_vehiculo": "CAMION",
  "estado": "DISPONIBLE"
}
```

### JSON: `asignaciones`

```json
{
  "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "conductor_id": "11111111-1111-1111-1111-111111111111",
  "vehiculo_id": null,
  "tipo_vehiculo": "CAMION",
  "fecha_inicio": "2026-07-01",
  "fecha_fin": "2026-07-10",
  "creada_en": "2026-05-18T15:30:00Z"
}
```

> `vehiculo_id` es `null` al momento de la creación. Se llena cuando Vehículos confirma la asignación.

### JSON: `licencias`

```json
{
  "id": "dc912c19-25d1-4d29-be08-0f03f2459f45",
  "conductor_id": "11111111-1111-1111-1111-111111111111",
  "categoria": "C1",
  "fecha_vencimiento": "2029-03-12"
}
```

### JSON: `saga_registros`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "asignacion_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "estado": "COMPLETADO",
  "vehiculo_id": "11111111-1111-1111-1111-111211111111",
  "motivo_fallo": null,
  "creada_en": "2026-05-18T07:00:00Z",
  "actualizada_en": "2026-05-18T07:02:15Z"
}
```

---

## 4. Relación entre Tablas

```
conductores (1)──────────────(N) asignaciones
     │                              │
     │                              │
     └──(1)───(N) licencias         └──(1)──(1) saga_registros
```

- Un conductor puede tener múltiples licencias (`licencias.conductor_id`).
- Un conductor puede tener múltiples asignaciones a lo largo del tiempo (`asignaciones.conductor_id`).
- Cada asignación tiene exactamente un registro de trazabilidad SAGA (`saga_registros.asignacion_id`).

---

## 5. Estados del Dominio

### `EstadoConductor` (enum en `domain/enums/`)

| Valor | Significado |
|---|---|
| `DISPONIBLE` | El conductor puede recibir una nueva asignación. |
| `RESERVADO` | El conductor fue seleccionado y está en proceso de confirmación de vehículo (SAGA pendiente). |
| `INACTIVO` | El conductor no está operativo. |

### `EstadoSaga` (enum en `domain/enums/`)

| Valor | Significado |
|---|---|
| `PENDIENTE_VEHICULO` | La saga fue iniciada. Se publicó `VehiculoSolicitadoEvent` y se espera respuesta de Vehículos. |
| `PENDIENTE_LIBERACION` | Se recibió una falla mecánica. Se publicó `VehiculoLiberadoEvent` y se espera que Vehículos libere el vehículo. |
| `COMPLETADO` | Vehículos confirmó la asignación. La SAGA terminó exitosamente. |
| `FALLIDO` | Vehículos rechazó la solicitud. La compensación fue ejecutada (conductor liberado). |
