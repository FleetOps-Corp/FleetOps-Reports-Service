> Nota: Este documento contiene contratos preliminares para pruebas e integración.
> Las rutas API son propuestas y deben validarse con el equipo responsable del microservicio de Asignaciones.
> El PDF base define tablas, estados, flujos SAGA y payloads generales, pero no define rutas finales exactas.


# FleetOps — Microservicio de Asignaciones: Referencia Técnica

---

## 1. Base de Datos

### Tabla: `tabla_conductores`

Registra los conductores disponibles para ser asignados a vehículos.

| Columna           | Tipo           | Restricciones  | Descripción                       |
| ----------------- | -------------- | -------------- | --------------------------------- |
| `id_conductor`    | `VARCHAR(30)`  | CLAVE PRIMARIA | Identificador único del conductor |
| `nombre_completo` | `VARCHAR(255)` | NOT NULL       | Nombre completo del conductor     |
| `estado`          | `VARCHAR(30)`  | NOT NULL       | Estado operativo del conductor    |

### Estados del conductor

```txt
DISPONIBLE
RESERVADO
ASIGNADO
INCAPACITADO
```

| Estado         | Descripción                                                                                     |
| -------------- | ----------------------------------------------------------------------------------------------- |
| `DISPONIBLE`   | El conductor puede ser asignado a un vehículo                                                   |
| `RESERVADO`    | El conductor fue seleccionado temporalmente mientras se confirma la disponibilidad del vehículo |
| `ASIGNADO`     | El conductor tiene una asignación activa                                                        |
| `INCAPACITADO` | El conductor no puede operar por incapacidad humana                                             |

---

### Tabla: `tabla_tipo_vehiculos`

Registra los tipos de vehículos existentes en el sistema.

| Columna                | Tipo           | Restricciones  | Descripción                             |
| ---------------------- | -------------- | -------------- | --------------------------------------- |
| `id_tipo_vehiculo`     | `VARCHAR(10)`  | CLAVE PRIMARIA | Identificador del tipo de vehículo      |
| `nombre_tipo_vehiculo` | `VARCHAR(255)` | NOT NULL       | Nombre descriptivo del tipo de vehículo |

### Ejemplo de registros

| id_tipo_vehiculo | nombre_tipo_vehiculo |
| ---------------- | -------------------- |
| `A`              | Vehículo tipo A      |
| `B`              | Vehículo tipo B      |
| `C`              | Vehículo tipo C      |

---

### Tabla: `tabla_licencias`

Relaciona los conductores con los tipos de vehículos que están autorizados a operar.

| Columna            | Tipo          | Restricciones | Descripción                         |
| ------------------ | ------------- | ------------- | ----------------------------------- |
| `id_conductor`     | `VARCHAR(30)` | CLAVE FORÁNEA | ID del conductor                    |
| `id_tipo_vehiculo` | `VARCHAR(10)` | CLAVE FORÁNEA | Tipo de vehículo que puede conducir |

### Ejemplo de registros

| id_conductor | id_tipo_vehiculo |
| ------------ | ---------------- |
| `13010`      | `A`              |
| `13010`      | `C`              |

---

### Tabla: `tabla_asignaciones`

Registra las asignaciones de conductores a vehículos.

| Columna         | Tipo                 | Restricciones  | Descripción                                           |
| --------------- | -------------------- | -------------- | ----------------------------------------------------- |
| `id_asignacion` | `VARCHAR(30)`        | CLAVE PRIMARIA | Identificador único de la asignación                  |
| `id_conductor`  | `VARCHAR(30)`        | CLAVE FORÁNEA  | Conductor asignado                                    |
| `id_vehiculo`   | `VARCHAR(30)`        | CLAVE FORÁNEA  | Vehículo asignado desde el microservicio de Vehículos |
| `fecha_inicio`  | `DATE` o `TIMESTAMP` | NOT NULL       | Fecha de inicio de la asignación                      |
| `fecha_fin`     | `DATE` o `TIMESTAMP` | NOT NULL       | Fecha de finalización de la asignación                |
| `estado`        | `VARCHAR(30)`        | NOT NULL       | Estado actual de la asignación                        |

### Estados de la asignación

```txt
ACTIVO
FINALIZADO
CANCELADO
```

| Estado       | Descripción                                    |
| ------------ | ---------------------------------------------- |
| `ACTIVO`     | La asignación está vigente                     |
| `FINALIZADO` | La asignación terminó correctamente            |
| `CANCELADO`  | La asignación fue cancelada antes de finalizar |

### Ejemplo de registro

| id_asignacion | id_conductor | id_vehiculo | fecha_inicio | fecha_fin    | estado   |
| ------------- | ------------ | ----------- | ------------ | ------------ | -------- |
| `asig_1`      | `13010`      | `ABC123`    | `2026-05-18` | `2026-05-20` | `ACTIVO` |

---

### Tabla: `tabla_SAGA`

Registra el estado de la orquestación SAGA durante la creación, modificación o cancelación de asignaciones.

| Columna          | Tipo          | Restricciones  | Descripción                                    |
| ---------------- | ------------- | -------------- | ---------------------------------------------- |
| `id_saga`        | `VARCHAR(30)` | CLAVE PRIMARIA | Identificador único de la transacción SAGA     |
| `id_asignacion`  | `VARCHAR(30)` | CLAVE FORÁNEA  | Asignación relacionada con la SAGA             |
| `estado`         | `VARCHAR(50)` | NOT NULL       | Estado actual de la orquestación               |
| `ultimo_error`   | `TEXT`        | NULL           | Último error registrado durante la transacción |
| `contador_retry` | `INTEGER`     | DEFAULT 0      | Número de reintentos realizados                |

### Estados de la SAGA

```txt
PENDIENTE_CONFIRMACION_VEHICULO
COMPLETADO
FALLIDO
CANCELADO
```

| Estado                            | Descripción                                                              |
| --------------------------------- | ------------------------------------------------------------------------ |
| `PENDIENTE_CONFIRMACION_VEHICULO` | La asignación está esperando confirmación del microservicio de Vehículos |
| `COMPLETADO`                      | La transacción terminó exitosamente                                      |
| `FALLIDO`                         | La transacción no pudo completarse y se ejecutó compensación             |
| `CANCELADO`                       | La asignación fue cancelada                                              |

### Ejemplo de registro

| id_saga  | id_asignacion | estado       | ultimo_error | contador_retry |
| -------- | ------------- | ------------ | ------------ | -------------- |
| `saga_1` | `asig_1`      | `COMPLETADO` | `None`       | `0`            |

---

## 2. Endpoints de la API — Respuestas JSON

> Nota: Los siguientes endpoints son una propuesta preliminar para documentación y pruebas. Deben validarse con la implementación real del microservicio.

---

### `POST /api/asignaciones/create/`

Crear una nueva asignación de conductor y vehículo.

Este flujo inicia una orquestación SAGA. El microservicio de Asignaciones busca un conductor disponible que pueda manejar el tipo de vehículo solicitado, lo reserva temporalmente y solicita al microservicio de Vehículos un vehículo disponible de ese tipo.

**Autenticación:** Token JWT Bearer requerido.

**Cuerpo de la solicitud:**

```json
{
    "tipo_vehiculo": "A",
    "fecha_inicio": "2026-06-25T08:00:00",
    "fecha_fin": "2026-06-27T18:00:00"
}
```

| Campo           | Requerido | Valores                                            |
| --------------- | --------- | -------------------------------------------------- |
| `tipo_vehiculo` | ✅         | Tipo de vehículo requerido. Ejemplo: `A`, `B`, `C` |
| `fecha_inicio`  | ✅         | Fecha y hora de inicio en formato ISO 8601         |
| `fecha_fin`     | ✅         | Fecha y hora de finalización en formato ISO 8601   |

**Respuesta `201 Created`:**

```json
{
    "id_asignacion": "asig_1",
    "id_saga": "saga_1",
    "id_conductor": "13010",
    "id_vehiculo": "ABC123",
    "tipo_vehiculo": "A",
    "fecha_inicio": "2026-06-25T08:00:00",
    "fecha_fin": "2026-06-27T18:00:00",
    "estado": "ACTIVO",
    "estado_saga": "COMPLETADO"
}
```

**Respuesta cuando no hay conductor disponible:**

```json
{
    "detail": "No hay conductores disponibles para el tipo de vehículo solicitado."
}
```

**Respuesta cuando no hay vehículo disponible:**

```json
{
    "id_saga": "saga_1",
    "estado_saga": "FALLIDO",
    "detail": "No hay vehículos disponibles del tipo solicitado."
}
```

---

### `GET /api/asignaciones/`

Consultar asignaciones registradas.

**Autenticación:** No requerida o según política del sistema.

**Parámetros de consulta opcionales:**

| Parámetro      | Valores                             | Ejemplo                            |
| -------------- | ----------------------------------- | ---------------------------------- |
| `estado`       | `ACTIVO`, `FINALIZADO`, `CANCELADO` | `?estado=ACTIVO`                   |
| `id_conductor` | Cualquier ID de conductor           | `?id_conductor=13010`              |
| `id_vehiculo`  | Cualquier ID de vehículo            | `?id_vehiculo=ABC123`              |
| `fecha_desde`  | Fecha ISO 8601                      | `?fecha_desde=2026-06-01T00:00:00` |
| `fecha_hasta`  | Fecha ISO 8601                      | `?fecha_hasta=2026-06-30T23:59:59` |

**Ejemplos de consultas:**

```txt
GET /api/asignaciones/
GET /api/asignaciones/?estado=ACTIVO
GET /api/asignaciones/?id_conductor=13010
GET /api/asignaciones/?id_vehiculo=ABC123
GET /api/asignaciones/?fecha_desde=2026-06-01T00:00:00&fecha_hasta=2026-06-30T23:59:59
```

**Respuesta `200 OK`:**

```json
[
    {
        "id_asignacion": "asig_1",
        "id_conductor": "13010",
        "id_vehiculo": "ABC123",
        "fecha_inicio": "2026-06-25T08:00:00",
        "fecha_fin": "2026-06-27T18:00:00",
        "estado": "ACTIVO"
    },
    {
        "id_asignacion": "asig_2",
        "id_conductor": "13011",
        "id_vehiculo": "XYZ456",
        "fecha_inicio": "2026-06-20T08:00:00",
        "fecha_fin": "2026-06-21T18:00:00",
        "estado": "FINALIZADO"
    }
]
```

Retorna una lista vacía `[]` si no existen asignaciones que coincidan con los filtros.

---

### `GET /api/asignaciones/{id_asignacion}/`

Obtener una asignación específica por su ID.

**Autenticación:** No requerida o según política del sistema.

**Parámetro de URL:** `id_asignacion`

**Ejemplo:**

```txt
GET /api/asignaciones/asig_1/
```

**Respuesta `200 OK`:**

```json
{
    "id_asignacion": "asig_1",
    "id_conductor": "13010",
    "id_vehiculo": "ABC123",
    "fecha_inicio": "2026-06-25T08:00:00",
    "fecha_fin": "2026-06-27T18:00:00",
    "estado": "ACTIVO"
}
```

---

### `PUT /api/asignaciones/incapacidad-humana/`

Modificar una asignación por incapacidad humana del conductor.

Este endpoint es usado cuando el microservicio de Incidentes reporta una incapacidad humana. Asignaciones debe cambiar el estado del conductor afectado a `INCAPACITADO` y buscar un conductor disponible que pueda manejar el mismo tipo de vehículo.

**Autenticación:** Servicio interno o Token JWT Bearer requerido.

**Cuerpo de la solicitud:**

```json
{
    "id_asignacion": "asig_1",
    "id_conductor": "13010"
}
```

| Campo           | Requerido | Descripción            |
| --------------- | --------- | ---------------------- |
| `id_asignacion` | ✅         | Asignación afectada    |
| `id_conductor`  | ✅         | Conductor incapacitado |

**Respuesta `200 OK`:**

```json
{
    "id_asignacion": "asig_1",
    "id_conductor_anterior": "13010",
    "id_conductor_nuevo": "13015",
    "estado_conductor_anterior": "INCAPACITADO",
    "estado_conductor_nuevo": "ASIGNADO",
    "estado_asignacion": "ACTIVO",
    "message": "Conductor reasignado correctamente por incapacidad humana."
}
```

---

### `POST /api/asignaciones/disponibilizar-conductor/`

Cambiar a disponible un conductor que estaba incapacitado.

**Autenticación:** Token JWT Bearer requerido.

**Cuerpo de la solicitud:**

```json
{
    "id_conductor": "13010"
}
```

| Campo          | Requerido | Descripción                                |
| -------------- | --------- | ------------------------------------------ |
| `id_conductor` | ✅         | Conductor que será marcado como disponible |

**Respuesta `200 OK`:**

```json
{
    "id_conductor": "13010",
    "estado": "DISPONIBLE",
    "message": "Conductor marcado como disponible correctamente."
}
```

---

### `PUT /api/asignaciones/falla-mecanica/`

Modificar una asignación por falla mecánica del vehículo.

Este flujo se ejecuta cuando el microservicio de Incidentes reporta una falla mecánica. Primero se solicita al microservicio de Vehículos cambiar el estado del vehículo afectado a `FALLA_MECANICA`. Luego Asignaciones solicita un nuevo vehículo disponible del mismo tipo y actualiza la asignación.

**Autenticación:** Servicio interno o Token JWT Bearer requerido.

**Cuerpo de la solicitud:**

```json
{
    "id_asignacion": "asig_1",
    "id_vehiculo": "ABC123"
}
```

| Campo           | Requerido | Descripción                          |
| --------------- | --------- | ------------------------------------ |
| `id_asignacion` | ✅         | Asignación afectada                  |
| `id_vehiculo`   | ✅         | Vehículo que presentó falla mecánica |

**Respuesta `200 OK`:**

```json
{
    "id_asignacion": "asig_1",
    "id_saga": "saga_2",
    "id_vehiculo_anterior": "ABC123",
    "id_vehiculo_nuevo": "XYZ456",
    "estado_asignacion": "ACTIVO",
    "estado_saga": "COMPLETADO",
    "message": "Vehículo reasignado correctamente por falla mecánica."
}
```

---

### `DELETE /api/asignaciones/{id_asignacion}/`

Cancelar una asignación existente.

Al cancelar una asignación, Asignaciones solicita al microservicio de Vehículos liberar el vehículo asociado para devolverlo a estado `DISPONIBLE`. Luego ejecuta una transacción local para cambiar la asignación a `CANCELADO`, cambiar el conductor a `DISPONIBLE` y marcar la SAGA como `CANCELADO`.

**Autenticación:** Token JWT Bearer requerido.

**Parámetro de URL:** `id_asignacion`

**Ejemplo:**

```txt
DELETE /api/asignaciones/asig_1/
```

**Respuesta `200 OK`:**

```json
{
    "id_asignacion": "asig_1",
    "id_saga": "saga_1",
    "id_conductor": "13010",
    "id_vehiculo": "ABC123",
    "estado_asignacion": "CANCELADO",
    "estado_conductor": "DISPONIBLE",
    "estado_saga": "CANCELADO",
    "message": "Asignación cancelada correctamente."
}
```

---

## 3. Integración con el Microservicio de Vehículos

El microservicio de Asignaciones se comunica con el microservicio de Vehículos para solicitar y liberar vehículos.

---

### Solicitud de vehículo disponible

**Destino:** Microservicio de Vehículos

**Método propuesto:** `POST /api/vehicles/assign/`

**Payload enviado:**

```json
{
    "id_saga": "saga_1",
    "tipo_vehiculo": "A"
}
```

| Campo           | Tipo     | Descripción                                |
| --------------- | -------- | ------------------------------------------ |
| `id_saga`       | `string` | Identificador único de la transacción SAGA |
| `tipo_vehiculo` | `string` | Tipo de vehículo requerido                 |

**Respuesta esperada `200 OK`:**

```json
{
    "id_saga": "saga_1",
    "id_vehiculo": "ABC123",
    "tipo_vehiculo": "A",
    "estado": "ASIGNADO"
}
```

---

### Liberación de vehículo

**Destino:** Microservicio de Vehículos

**Método propuesto:** `POST /api/vehicles/release/`

**Payload enviado:**

```json
{
    "id_saga": "saga_1",
    "id_vehiculo": "ABC123"
}
```

| Campo         | Tipo     | Descripción                                 |
| ------------- | -------- | ------------------------------------------- |
| `id_saga`     | `string` | Identificador único de la transacción SAGA  |
| `id_vehiculo` | `string` | Vehículo que debe volver a estar disponible |

**Respuesta esperada `200 OK`:**

```json
{
    "id_saga": "saga_1",
    "id_vehiculo": "ABC123",
    "estado": "DISPONIBLE"
}
```

---

### Cambio de estado por falla mecánica

**Destino:** Microservicio de Vehículos

**Método propuesto:** `PUT /api/vehicles/mechanical-failure/`

**Payload enviado:**

```json
{
    "id_vehiculo": "ABC123"
}
```

**Respuesta esperada `200 OK`:**

```json
{
    "id_vehiculo": "ABC123",
    "estado": "FALLA_MECANICA"
}
```

---

## 4. Flujo de Orquestación SAGA

### Flujo de creación de una asignación

1. El Administrador o Coordinador envía una solicitud:

```json
{
    "tipo_vehiculo": "A",
    "fecha_inicio": "2026-06-25T08:00:00",
    "fecha_fin": "2026-06-27T18:00:00"
}
```

2. Asignaciones ejecuta una transacción local ACID:

```txt
- Buscar un conductor DISPONIBLE que pueda manejar el tipo_vehiculo solicitado.
- Cambiar su estado a RESERVADO.
- Crear un registro SAGA con estado PENDIENTE_CONFIRMACION_VEHICULO.
```

3. Asignaciones solicita a Vehículos un vehículo disponible:

```json
{
    "id_saga": "saga_1",
    "tipo_vehiculo": "A"
}
```

4. Vehículos cambia el estado del vehículo a `ASIGNADO` y devuelve el `id_vehiculo`.

5. Asignaciones ejecuta una segunda transacción local ACID:

```txt
- Crear asignación con estado ACTIVO.
- Cambiar estado del conductor a ASIGNADO.
- Cambiar estado del registro SAGA a COMPLETADO.
```

6. Asignaciones responde al Administrador o Coordinador con `200 OK` o `201 Created`.

7. Cuando llega la fecha de finalización de la asignación, Asignaciones solicita a Vehículos liberar el vehículo.

8. Vehículos responde `200 OK`.

9. Asignaciones finaliza localmente la asignación:

```txt
- Cambiar estado de la asignación a FINALIZADO.
- Cambiar estado del conductor a DISPONIBLE.
```

---

## 5. Mecanismos de Compensación en Orquestación SAGA

### 1. Falla al solicitar un vehículo

Ocurre cuando Asignaciones no logra comunicarse con Vehículos al solicitar un vehículo disponible.

**Compensación:**

```txt
- Realizar varios reintentos durante un tiempo límite definido.
- Si no se logra comunicación:
  - Cambiar el conductor reservado a DISPONIBLE.
  - Marcar el registro SAGA como FALLIDO.
```

---

### 2. No existen vehículos disponibles

Ocurre cuando Vehículos responde correctamente, pero indica que no existe ningún vehículo disponible del tipo solicitado.

**Compensación:**

```txt
- Cambiar el conductor reservado a DISPONIBLE.
- Marcar el registro SAGA como FALLIDO.
```

---

### 3. Vehículos asigna el vehículo, pero la respuesta no llega

Ocurre cuando Vehículos asigna correctamente el vehículo y lo cambia a `ASIGNADO`, pero por un fallo de red la respuesta no llega a Asignaciones.

**Manejo por idempotencia:**

```txt
- Cada petición incluye un id_saga único.
- Vehículos guarda los id_saga ya procesados.
- Si Asignaciones reintenta con el mismo id_saga:
  - No se asigna un nuevo vehículo.
  - Se devuelve el mismo vehículo previamente asignado.
```

Esto evita asignaciones duplicadas y permite que los reintentos sean seguros.

---

### 4. Falla en la última transacción ACID local

Ocurre cuando Vehículos ya asignó correctamente el vehículo y devolvió el `id_vehiculo`, pero ocurre un error durante la transacción local final de Asignaciones.

**Compensación:**

```txt
- Reintentar la operación local.
- Si después de varios intentos la transacción sigue fallando:
  - Cambiar el conductor a DISPONIBLE.
  - Marcar la SAGA como FALLIDO.
  - Solicitar a Vehículos liberar el vehículo.
```

---

### 5. Falla al liberar el vehículo al finalizar la asignación

Ocurre cuando la asignación termina y Asignaciones solicita a Vehículos liberar el vehículo, pero la respuesta no llega.

**Manejo por idempotencia:**

```txt
- Cada petición incluye un id_saga único.
- Vehículos guarda los id_saga ya procesados.
- Si Asignaciones reintenta la liberación con el mismo id_saga:
  - Vehículos detecta que la operación ya fue procesada.
  - Responde de forma segura sin alterar nuevamente el estado del vehículo.
```

---

## 6. Flujos de Modificación

### Modificación por incapacidad humana

Este flujo se dispara desde el microservicio de Incidentes cuando se reporta un incidente de tipo humano que incapacita al conductor.

**Solicitud recibida desde Incidentes:**

```json
{
    "id_asignacion": "asig_1",
    "id_conductor": "13010"
}
```

**Transacción local ACID en Asignaciones:**

```txt
- Cambiar estado del conductor afectado a INCAPACITADO.
- Buscar un conductor DISPONIBLE que pueda manejar el mismo tipo de vehículo.
- Cambiar el nuevo conductor a ASIGNADO.
- Actualizar la asignación con el nuevo id_conductor.
```

**Respuesta `200 OK`:**

```json
{
    "id_asignacion": "asig_1",
    "id_conductor_anterior": "13010",
    "id_conductor_nuevo": "13015",
    "estado": "ACTIVO",
    "message": "Asignación modificada por incapacidad humana."
}
```

---

### Disponibilizar conductor incapacitado

Este flujo lo ejecuta un Administrador o Coordinador cuando un conductor incapacitado vuelve a estar disponible.

**Solicitud:**

```json
{
    "id_conductor": "13010"
}
```

**Acción:**

```txt
- Cambiar estado del conductor a DISPONIBLE.
```

**Respuesta `200 OK`:**

```json
{
    "id_conductor": "13010",
    "estado": "DISPONIBLE",
    "message": "Conductor disponibilizado correctamente."
}
```

---

### Modificación por falla mecánica

Este flujo se dispara desde el microservicio de Incidentes cuando se reporta una falla mecánica de un vehículo.

**Paso 1 — Incidentes solicita a Vehículos marcar falla mecánica:**

```json
{
    "id_vehiculo": "ABC123"
}
```

**Respuesta esperada de Vehículos:**

```json
{
    "id_vehiculo": "ABC123",
    "estado": "FALLA_MECANICA"
}
```

**Paso 2 — Incidentes solicita a Asignaciones cambiar el vehículo de la asignación:**

```json
{
    "id_asignacion": "asig_1",
    "id_vehiculo": "ABC123"
}
```

**Acciones en Asignaciones:**

```txt
- Crear registro SAGA con estado PENDIENTE_CONFIRMACION_VEHICULO.
- Solicitar a Vehículos un nuevo vehículo disponible del mismo tipo.
- Vehículos cambia el nuevo vehículo a ASIGNADO y devuelve id_vehiculo.
- Asignaciones cambia el id_vehiculo en la asignación afectada.
- Marcar la SAGA como COMPLETADO.
```

**Respuesta `200 OK`:**

```json
{
    "id_asignacion": "asig_1",
    "id_vehiculo_anterior": "ABC123",
    "id_vehiculo_nuevo": "XYZ456",
    "estado_saga": "COMPLETADO",
    "message": "Vehículo reasignado correctamente por falla mecánica."
}
```

---

## 7. Flujo de Cancelación de Asignación

Este flujo permite cancelar una asignación activa.

**Solicitud:**

```txt
DELETE /api/asignaciones/asig_1/
```

**Acciones del flujo:**

1. El Administrador o Coordinador solicita cancelar la asignación.
2. Asignaciones solicita a Vehículos cambiar el vehículo a `DISPONIBLE`.
3. Vehículos responde `200 OK`.
4. Asignaciones ejecuta una transacción local ACID:

```txt
- Cambiar estado del registro SAGA a CANCELADO.
- Cambiar estado de la asignación a CANCELADO.
- Cambiar estado del conductor a DISPONIBLE.
```

**Respuesta `200 OK`:**

```json
{
    "id_asignacion": "asig_1",
    "id_saga": "saga_1",
    "estado_asignacion": "CANCELADO",
    "estado_saga": "CANCELADO",
    "estado_conductor": "DISPONIBLE",
    "message": "Asignación cancelada correctamente."
}
```

---

## 8. Eventos / Mensajes entre Microservicios

> Nota: En el PDF se muestra comunicación entre microservicios mediante solicitudes entre Asignaciones, Vehículos e Incidentes. Si el equipo decide usar RabbitMQ, estos eventos pueden documentarse como contratos preliminares.

---

### Evento: `assignment_created`

Se publica cuando una asignación se crea correctamente.

**Payload propuesto:**

```json
{
    "event": "assignment_created",
    "id_asignacion": "asig_1",
    "id_saga": "saga_1",
    "id_conductor": "13010",
    "id_vehiculo": "ABC123",
    "fecha_inicio": "2026-06-25T08:00:00",
    "fecha_fin": "2026-06-27T18:00:00",
    "estado": "ACTIVO",
    "fecha_evento": "2026-06-25T08:00:01"
}
```

---

### Evento: `assignment_cancelled`

Se publica cuando una asignación es cancelada.

**Payload propuesto:**

```json
{
    "event": "assignment_cancelled",
    "id_asignacion": "asig_1",
    "id_saga": "saga_1",
    "id_conductor": "13010",
    "id_vehiculo": "ABC123",
    "estado": "CANCELADO",
    "fecha_evento": "2026-06-25T10:30:00"
}
```

---

### Evento: `driver_reassigned`

Se publica cuando un conductor es reemplazado por incapacidad humana.

**Payload propuesto:**

```json
{
    "event": "driver_reassigned",
    "id_asignacion": "asig_1",
    "id_conductor_anterior": "13010",
    "id_conductor_nuevo": "13015",
    "motivo": "INCAPACIDAD_HUMANA",
    "fecha_evento": "2026-06-25T11:00:00"
}
```

---

### Evento: `vehicle_reassigned`

Se publica cuando un vehículo es reemplazado por falla mecánica.

**Payload propuesto:**

```json
{
    "event": "vehicle_reassigned",
    "id_asignacion": "asig_1",
    "id_vehiculo_anterior": "ABC123",
    "id_vehiculo_nuevo": "XYZ456",
    "motivo": "FALLA_MECANICA",
    "fecha_evento": "2026-06-25T12:00:00"
}
```

---

## 9. Suposición Operativa Acordada

Existe al menos el doble de conductores capacitados para operar un tipo de vehículo específico en comparación con la cantidad de vehículos de dicho tipo. Esto garantiza disponibilidad de conductores de reemplazo ante reasignaciones por incapacidad humana.

---

## 10. Observaciones Técnicas

* El microservicio de Asignaciones actúa como orquestador SAGA.
* La asignación de vehículos depende del microservicio de Vehículos.
* Los incidentes humanos y mecánicos pueden modificar asignaciones activas.
* Los reintentos deben ser idempotentes usando `id_saga`.
* El estado `RESERVADO` evita que un mismo conductor sea tomado por varias asignaciones simultáneamente.
* Las compensaciones deben devolver el sistema a un estado consistente cuando falla una operación distribuida.
* Los nombres de endpoints y eventos son preliminares y deben alinearse con la implementación final del equipo.
