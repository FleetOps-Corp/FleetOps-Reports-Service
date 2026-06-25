# FleetOps — Microservicio de Incidentes: Referencia Técnica

---

## 1. Base de Datos

### Tabla: `incidents`

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | `VARCHAR(30)` | CLAVE PRIMARIA | ID legible: `INC-20260621-a3f9` |
| `fecha_hora` | `TIMESTAMP` | NOT NULL | Fecha y hora del incidente |
| `id_conductor` | `VARCHAR(255)` | NOT NULL | ID del conductor del microservicio de Conductores |
| `placa_vehiculo` | `VARCHAR(20)` | NOT NULL | Placa del vehículo |
| `tipo_incidente` | `VARCHAR(20)` | NOT NULL | `HUMANO` o `MECANICO` |
| `gravedad` | `VARCHAR(20)` | NOT NULL | `LEVE` o `GRAVE` |
| `descripcion` | `TEXT` | NOT NULL | Descripción del incidente |
| `created_at` | `TIMESTAMP` | AUTO | Fecha de creación del registro |
| `updated_at` | `TIMESTAMP` | AUTO | Fecha de última actualización |

### Formato del ID

```
INC-{YYYYMMDD}-{SHORT_UUID}

INC      → prefijo fijo
FECHA    → fecha del incidente (YYYYMMDD)
UUID     → primeros 4 caracteres de un UUID (ej. a3f9)

Ejemplos:
  INC-20260621-a3f9
  INC-20260624-b7c2
```

---

## 2. Endpoints de la API — Respuestas JSON

### `POST /api/incidents/create/`

Registrar un nuevo incidente.

**Autenticación:** Token JWT Bearer requerido (`IsAuthenticated`)

**Cuerpo de la solicitud:**

```json
{
    "id_conductor": "CONDUCTOR-001",
    "placa_vehiculo": "ABC-123",
    "tipo_incidente": "MECANICO",
    "gravedad": "GRAVE",
    "descripcion": "El vehículo presentó falla en los frenos durante la ruta.",
    "fecha_hora": "2026-06-21T22:00:00"
}
```

| Campo | Requerido | Valores |
|---|---|---|
| `id_conductor` | ✅ | Cualquier cadena no vacía |
| `placa_vehiculo` | ✅ | Formato de placa ej. `ABC-123` (se normaliza a mayúsculas) |
| `tipo_incidente` | ✅ | `HUMANO` o `MECANICO` |
| `gravedad` | ✅ | `LEVE` o `GRAVE` |
| `descripcion` | ✅ | Cualquier texto |
| `fecha_hora` | ✅ | Fecha y hora en formato ISO 8601, por defecto la hora actual |

**Respuesta `201 Created`:**

```json
{
    "id": "INC-MEC-GRV-20260621-a3f9",
    "fecha_hora": "2026-06-21T22:00:00",
    "id_conductor": "CONDUCTOR-001",
    "placa_vehiculo": "ABC-123",
    "tipo_incidente": "MECANICO",
    "gravedad": "GRAVE",
    "descripcion": "El vehículo presentó falla en los frenos durante la ruta.",
    "created_at": "2026-06-21T22:00:01.123456",
    "updated_at": "2026-06-21T22:00:01.123456"
}
```

---

### `GET /api/incidents/`

Consultar incidentes con filtros opcionales.

**Autenticación:** No requerida (`AllowAny`)

**Parámetros de consulta (todos opcionales y combinables):**

| Parámetro | Valores | Ejemplo |
|---|---|---|
| `tipo_incidente` | `HUMANO`, `MECANICO` | `?tipo_incidente=MECANICO` |
| `gravedad` | `LEVE`, `GRAVE` | `?gravedad=GRAVE` |
| `placa` | Cualquier placa | `?placa=ABC-123` |
| `id_conductor` | Cualquier cadena | `?id_conductor=CONDUCTOR-001` |
| `fecha_desde` | Fecha ISO 8601 | `?fecha_desde=2026-06-01T00:00:00` |
| `fecha_hasta` | Fecha ISO 8601 | `?fecha_hasta=2026-06-24T23:59:59` |

**Ejemplos de consultas:**

```
GET /api/incidents/
GET /api/incidents/?tipo_incidente=MECANICO
GET /api/incidents/?gravedad=GRAVE&tipo_incidente=MECANICO
GET /api/incidents/?placa=ABC-123&gravedad=GRAVE
GET /api/incidents/?id_conductor=CONDUCTOR-001
GET /api/incidents/?fecha_desde=2026-06-01T00:00:00&fecha_hasta=2026-06-24T23:59:59
GET /api/incidents/?tipo_incidente=HUMANO&fecha_desde=2026-06-01T00:00:00
```

**Respuesta `200 OK`:**

```json
[
    {
        "id": "INC-MEC-GRV-20260621-a3f9",
        "fecha_hora": "2026-06-21T22:00:00",
        "id_conductor": "CONDUCTOR-001",
        "placa_vehiculo": "ABC-123",
        "tipo_incidente": "MECANICO",
        "gravedad": "GRAVE",
        "descripcion": "Falla en los frenos.",
        "created_at": "2026-06-21T22:00:01.123456",
        "updated_at": "2026-06-21T22:00:01.123456"
    },
    {
        "id": "INC-HUM-LEV-20260622-c4d1",
        "fecha_hora": "2026-06-22T10:30:00",
        "id_conductor": "CONDUCTOR-002",
        "placa_vehiculo": "XYZ-456",
        "tipo_incidente": "HUMANO",
        "gravedad": "LEVE",
        "descripcion": "El evento fue que me mori",
        "created_at": "2026-06-22T10:30:05.654321",
        "updated_at": "2026-06-22T10:30:05.654321"
    }
]
```

Retorna una lista vacía `[]` si ningún incidente coincide con los filtros.

---

### `GET /api/incidents/{incident_id}/`

Obtener un incidente específico por su ID.

**Autenticación:** No requerida (`AllowAny`)

**Parámetro de URL:** `incident_id` — el ID completo del incidente ej. `INC-20260621-a3f9`

**Ejemplo:**

```
GET /api/incidents/INC-MEC-GRV-20260621-a3f9/
```

**Respuesta `200 OK`:**

```json
{
    "id": "INC-MEC-GRV-20260621-a3f9",
    "fecha_hora": "2026-06-21T22:00:00",
    "id_conductor": "CONDUCTOR-001",
    "placa_vehiculo": "ABC-123",
    "tipo_incidente": "MECANICO",
    "gravedad": "GRAVE",
    "descripcion": "Falla en los frenos.",
    "created_at": "2026-06-21T22:00:01.123456",
    "updated_at": "2026-06-21T22:00:01.123456"
}
```

---

## 3. Eventos RabbitMQ

### Evento: `incident_registered`

Se publica cada vez que un nuevo incidente es creado y persistido exitosamente. 

**Cola/Exchange:** `incident_registered`

**Publicado por:** `RabbitMQProducer.publish_incident_registered()`

**Disparado por:** `IncidentService._publish_incident_registered_event()`

**Payload:**

```json
{
    "incident_id": "INC-MEC-GRV-20260621-a3f9",
    "id_conductor": "CONDUCTOR-001",
    "placa_vehiculo": "ABC-123",
    "tipo_incidente": "MECANICO",
    "gravedad": "GRAVE",
    "descripcion": "Falla en los frenos.",
    "fecha_evento": "2026-06-21T22:00:01.123456"
}
```

| Campo | Tipo | Descripción |
|---|---|---|
| `incident_id` | `string` | ID generado del incidente |
| `id_conductor` | `string` | Conductor involucrado |
| `placa_vehiculo` | `string` | Placa del vehículo |
| `tipo_incidente` | `string` | `HUMANO` o `MECANICO` |
| `gravedad` | `string` | `LEVE` o `GRAVE` |
| `descripcion` | `string \| null` | Descripción opcional |
| `fecha_evento` | `string` | Marca de tiempo UTC de cuando se publicó el evento |

### Consumidores del evento

on building . . .
