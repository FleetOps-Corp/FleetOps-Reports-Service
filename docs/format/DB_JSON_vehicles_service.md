Aquí tienes el esquema técnico de tu microservicio de vehículos (**FleetOps**) completamente reorganizado y estructurado bajo el formato solicitado, detallando cada tabla, sus restricciones, la lógica de sus identificadores y ejemplos de su representación en formato JSON.

---

## 1. Base de Datos

### Tabla: `tipos_vehiculo` (Catálogo Maestro)

| Columna | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `id_tipo_vehiculo` | `BIGSERIAL` | PRIMARY KEY | Clave primaria autoincremental de 8 bytes para consultas rápidas. |
| `nombre_tipo` | `VARCHAR(100)` | NOT NULL, UNIQUE | Restricción de unicidad estricta para mitigar duplicación. |
| `descripcion` | `VARCHAR(255)` | NOT NULL | Breve descripción del tipo de vehículo. |
| `capacidad_carga` | `DOUBLE PRECISION` | NOT NULL | Expresado en kilogramos (Kg), soporta valores decimales. |
| `creado_en` | `TIMESTAMP` | NOT NULL, DEFAULT | Fecha y hora de creación (`CURRENT_TIMESTAMP`). |
| `actualizado_en` | `TIMESTAMP` | NULL | Fecha de última modificación. |

### Tabla: `vehiculos` (Agregado Raíz)

| Columna | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `id_vehiculo` | `UUID` | PRIMARY KEY, DEFAULT | Identificador global inmutable generado mediante `gen_random_uuid()`. |
| `numero_placa` | `VARCHAR(20)` | NOT NULL, UNIQUE | Placa de identificación del vehículo. Índice B-Tree asignado. |
| `marca` | `VARCHAR(100)` | NOT NULL | Fabricante de la unidad. |
| `modelo` | `VARCHAR(100)` | NOT NULL | Modelo comercial del vehículo. |
| `anio_fabricacion` | `INTEGER` | NOT NULL | Año de fabricación. |
| `color` | `VARCHAR(50)` | NOT NULL | Color de la carrocería. |
| `numero_chasis` | `VARCHAR(100)` | NOT NULL, UNIQUE | Regla de negocio #9: Número de chasis único. |
| `numero_motor` | `VARCHAR(100)` | NOT NULL, UNIQUE | Regla de negocio #13: Número de motor único. |
| `kilometraje` | `INTEGER` | NOT NULL, DEFAULT 0 | Kilometraje acumulado. |
| `ciudad_operacion` | `VARCHAR(100)` | NOT NULL | Ciudad asignada para operar. |
| `sede_operacion` | `VARCHAR(100)` | NOT NULL | Sede física/patio de operación. |
| `estado_vehiculo` | `VARCHAR(20)` | NOT NULL, DEFAULT | Restricción CHECK: `DISPONIBLE`, `RESERVADO`, `EN_MANTENIMIENTO`, `FUERA_DE_SERVICIO`. |
| `fecha_soat` | `DATE` | NOT NULL | Fecha de vencimiento del seguro obligatorio (SOAT). |
| `fecha_rtm` | `DATE` | NOT NULL | Fecha de vencimiento de la Revisión Tecnicomecánica. |
| `fecha_ultimo_mant` | `DATE` | NOT NULL | Fecha en la que se realizó el último mantenimiento técnico. |
| `activo` | `BOOLEAN` | NOT NULL, DEFAULT TRUE | Bandera para borrado lógico (*Soft Delete*). Índice asignado. |
| `creado_en` | `TIMESTAMP` | NOT NULL, DEFAULT | Fecha y hora de creación de la entidad. |
| `actualizado_en` | `TIMESTAMP` | NULL | Fecha de última modificación de la entidad. |
| `version` | `BIGINT` | NOT NULL, DEFAULT 0 | Token numérico para control de Concurrencia Optimista. |
| `id_tipo_vehiculo` | `BIGINT` | FOREIGN KEY | Referencia al catálogo maestro `tipos_vehiculo`. |

### Tabla: `historial_estados_vehiculo` (Auditoría Forense)

| Columna | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `id_historial` | `UUID` | PRIMARY KEY, DEFAULT | UUID v4 inmutable de la traza de auditoría. |
| `id_vehiculo` | `UUID` | NOT NULL, FK | Relación con `vehiculos` con regla `ON DELETE CASCADE`. |
| `estado_anterior` | `VARCHAR(30)` | NOT NULL | Estado previo del activo físico. |
| `estado_nuevo` | `VARCHAR(30)` | NOT NULL | Estado asignado post-transacción. |
| `motivo_cambio` | `VARCHAR(255)` | NOT NULL | Justificación del cambio de estado. |
| `servicio_origen` | `VARCHAR(100)` | NOT NULL | Microservicio o componente que gatilló el evento. |
| `id_correlacion` | `VARCHAR(100)` | NULL | ID cruzado para trazabilidad distribuida. |
| `registrado_en` | `TIMESTAMP` | NOT NULL, DEFAULT | Instante exacto del registro append-only. |

### Tabla: `sagas_vehiculo` (Distributed Saga Log)

| Columna | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `id_saga` | `UUID` | PRIMARY KEY, DEFAULT | UUID v4 de la instancia de la máquina de estados distribuida. |
| `id_vehiculo` | `UUID` | NOT NULL, FK | Relación con la entidad afectada de la flota. |
| `tipo_operacion` | `VARCHAR(50)` | NOT NULL | Nombre del proceso distribuido de negocio. |
| `estado_saga` | `VARCHAR(20)` | NOT NULL, DEFAULT | Restricción CHECK: `INICIADA`, `EN_PROGRESO`, `COMPLETADA`, `FALLIDA`, `COMPENSADA`. |
| `clave_idempotencia` | `VARCHAR(100)` | NOT NULL, UNIQUE | Barrera contra ataques de Replay e invocaciones duplicadas. |
| `intentos` | `INTEGER` | DEFAULT 1 | Contador de reintentos de pasos transaccionales. |
| `payload` | `TEXT` | NULL | Contexto operativo original serializado (Data Context). |
| `ultimo_error` | `TEXT` | NULL | Traza o mensaje del último fallo capturado. |
| `compensado_por` | `VARCHAR(100)` | NULL | Rol del usuario inmutable que firmó el Rollback/Compensación. |
| `version` | `BIGINT` | NOT NULL, DEFAULT 0 | Token de concurrencia optimista para el estado de la saga. |
| `creado_en` | `TIMESTAMP` | NOT NULL, DEFAULT | Inicio de la orquestación distribuida. |
| `actualizado_en` | `TIMESTAMP` | NULL | Último pulso de estado de la saga. |

### Tabla: `reservas_vehiculo` (Contratos Transaccionales)

| Columna | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `id_reserva` | `UUID` | PRIMARY KEY, DEFAULT | ID de la reserva. Frontera transaccional de asignación temporal. |
| `id_vehiculo` | `UUID` | NOT NULL, FK | Activo físico reservado. Índice asignado. |
| `id_saga` | `UUID` | NULL, FK | Relación opcional con la saga orquestadora correspondiente. |
| `id_asignacion_ext` | `UUID` | NULL | Llave lógica de correlación con microservicios satélites. |
| `estado_reserva` | `VARCHAR(20)` | NOT NULL, DEFAULT | Restricción CHECK: `PENDIENTE`, `CONFIRMADA`, `FALLIDA`, `CANCELADA`. |
| `clave_idempotencia` | `VARCHAR(100)` | NOT NULL, UNIQUE | Control para evitar duplicidad de solicitudes idénticas. Índice asignado. |
| `solicitado_por` | `VARCHAR(100)` | NOT NULL | Usuario o sistema que generó el contrato contractual. |
| `fecha_inicio` | `TIMESTAMP` | NOT NULL | Inicio de la ventana de asignación de activos. |
| `fecha_fin` | `TIMESTAMP` | NOT NULL | Fin de la ventana de asignación de activos. |
| `version` | `BIGINT` | NOT NULL, DEFAULT 0 | Bloqueo optimista gestionado en la capa de persistencia Java. |
| `creado_en` | `TIMESTAMP` | NOT NULL, DEFAULT | Fecha de registro de la reserva. |
| `actualizado_en` | `TIMESTAMP` | NULL | Fecha de última actualización del contrato. |

---

## 2. Formato de Identificadores (Identificación de Entidades)

### Tipos de Vehículo

```
[BIGSERIAL] → Incremental nativo secuencial (Base 10).
Ejemplo: 1, 2, 3...

```

### Vehículos / Historial / Sagas / Reservas

```
[UUID v4] → Formato estándar pseudoaleatorio de 36 caracteres cifrado vía pgcrypto.
Ejemplo: f3b9a528-72d1-4c12-ae9d-90cf41f8423d

```

---

## 3. Ejemplos de Representación JSON (Payloads de API)

### JSON: `tipos_vehiculo`

```json
{
  "id_tipo_vehiculo": 1,
  "nombre_tipo": "Tractocamión N3",
  "descripcion": "Vehículo pesado de carga articulado de más de 12 toneladas",
  "capacidad_carga": 32000.50,
  "creado_en": "2026-06-24T22:00:00Z",
  "actualizado_en": null
}

```

### JSON: `vehiculos`

```json
{
  "id_vehiculo": "8c12bda5-7482-4168-96ea-5fd3a9254c2a",
  "numero_placa": "TYX-789",
  "marca": "Kenworth",
  "modelo": "T800",
  "anio_fabricacion": 2024,
  "color": "Blanco Perlado",
  "numero_chasis": "1NKDF4DFXRP004123",
  "numero_motor": "ISX15-45012345",
  "kilometraje": 45200,
  "ciudad_operacion": "Bogotá",
  "sede_operacion": "Terminal Terrestre Norte",
  "estado_vehiculo": "DISPONIBLE",
  "fecha_soat": "2027-01-15",
  "fecha_rtm": "2027-03-20",
  "fecha_ultimo_mant": "2026-05-10",
  "activo": true,
  "creado_en": "2026-01-10T08:30:15Z",
  "actualizado_en": "2026-05-10T14:22:10Z",
  "version": 3,
  "id_tipo_vehiculo": 1
}

```

### JSON: `historial_estados_vehiculo`

```json
{
  "id_historial": "01af19c2-55fb-4299-9238-bd9d2c12519e",
  "id_vehiculo": "8c12bda5-7482-4168-96ea-5fd3a9254c2a",
  "estado_anterior": "DISPONIBLE",
  "estado_nuevo": "RESERVADO",
  "motivo_cambio": "Asignación automática por solicitud de viaje intermunicipal",
  "servicio_origen": "BookingOrchestratorService",
  "id_correlacion": "TX-SAG-991823-BOG",
  "registrado_en": "2026-06-24T22:58:00Z"
}

```

### JSON: `sagas_vehiculo`

```json
{
  "id_saga": "b8f05e6b-a2c3-4d44-8806-039c049ee411",
  "id_vehiculo": "8c12bda5-7482-4168-96ea-5fd3a9254c2a",
  "tipo_operacion": "RESERVA_FLOTA_TRIPARTITA",
  "estado_saga": "EN_PROGRESO",
  "clave_idempotencia": "IDEM-20260624-8c12bda5-001",
  "intentos": 1,
  "payload": "{\"routeId\":\"RT-882\",\"driverId\":\"DRV-1102\",\"estimatedHours\":14}",
  "ultimo_error": null,
  "compensated_por": null,
  "version": 1,
  "creado_en": "2026-06-24T22:57:45Z",
  "actualizado_en": "2026-06-24T22:58:00Z"
}

```

### JSON: `reservas_vehiculo`

```json
{
  "id_reserva": "ad45e128-4491-4a11-bfe3-9f1e403dcd22",
  "id_vehiculo": "8c12bda5-7482-4168-96ea-5fd3a9254c2a",
  "id_saga": "b8f05e6b-a2c3-4d44-8806-039c049ee411",
  "id_asignacion_ext": "e0915f0d-2b99-4676-92f7-7b2ee93c830a",
  "estado_reserva": "PENDIENTE",
  "clave_idempotencia": "IDEM-RESERVA-99210-2026",
  "solicitado_por": "Dispatcher_Core_Role",
  "fecha_inicio": "2026-06-25T06:00:00Z",
  "fecha_fin": "2026-06-25T20:00:00Z",
  "version": 0,
  "creado_en": "2026-06-24T22:58:00Z",
  "actualizado_en": null
}

```