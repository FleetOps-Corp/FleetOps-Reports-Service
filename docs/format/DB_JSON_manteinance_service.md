Aquí tienes la especificación técnica de este nuevo modelo (que parece estar asociado a la gestión de **Mantenimientos/Taller**), estructurado exactamente bajo el mismo estándar de diseño robusto, tipos nativos de PostgreSQL y auditoría concurrente que el resto de tu arquitectura de flota.

---

## 1. Base de Datos

### Tabla: `mantenimientos_vehiculo` (o el nombre físico asignado en tu servicio)

| Columna | Tipo | Restricciones | Descripción |
| --- | --- | --- | --- |
| `id_mantenimiento` | `UUID` | PRIMARY KEY, DEFAULT | Identificador único inmutable generado por `gen_random_uuid()`. |
| `id_vehiculo` | `UUID` | NOT NULL, FK | Relación con el Agregado Raíz `vehiculos`. |
| `id_incidente` | `UUID` | NULL | ID de correlación lógica con el microservicio de Incidentes (si aplica). |
| `tipo_mantenimiento` | `SMALLINT` | NOT NULL | Equivalente a `uint8`. Mapeo: `0` para Correctivo, `1` para Preventivo. |
| `gravedad` | `SMALLINT` | NOT NULL | Equivalente a `uint8`. Nivel de severidad asignado al ingreso. |
| `fecha_llegada` | `TIMESTAMP` | NOT NULL | Fecha y hora en la que el activo físico ingresa al patio/taller. |
| `fecha_inicio_mantenimiento` | `TIMESTAMP` | NOT NULL | Inicio formal de las actividades operativas de reparación o revisión. |
| `fecha_fin_mantenimiento` | `TIMESTAMP` | NULL | Finalización de los trabajos técnicos y liberación del vehículo. |
| `creado_en` | `TIMESTAMP` | NOT NULL, DEFAULT | Instante exacto en que se abre la orden en el sistema. |
| `actualizado_en` | `TIMESTAMP` | NULL | Fecha de la última modificación del registro. |
| `version` | `BIGINT` | NOT NULL, DEFAULT 0 | Token de Concurrencia Optimista (Optimistic Locking) para persistencia Java. |

> **Nota de Arquitectura:** En PostgreSQL, el tipo `uint8` (entero sin signo de 1 byte) se representa de forma óptima mediante `SMALLINT` para garantizar compatibilidad estándar, controlando el rango numérico mediante código o restricciones de check si se desea mitigar valores negativos.

---

## 2. Formato de Identificadores

```
[UUID v4] → Formato estándar estructurado de 36 caracteres.
Ejemplos de correlación de IDs:
  id_vehiculo   : 8c12bda5-7482-4168-96ea-5fd3a9254c2a
  id_incidente  : INC-20260624-b7c2 (o UUID según origen)

```

---

## 3. Ejemplo de Representación JSON (Payload de API)

### JSON: `mantenimientos_vehiculo`

```json
{
  "id_mantenimiento": "9e11fc4a-11bc-4e88-b223-38fa918bca44",
  "id_vehiculo": "8c12bda5-7482-4168-96ea-5fd3a9254c2a",
  "id_incidente": "4f9d12a3-7102-4bb3-bc55-102df93411cb",
  "tipo_mantenimiento": 0,
  "gravedad": 2,
  "fecha_llegada": "2026-06-24T18:30:00Z",
  "fecha_inicio_mantenimiento": "2026-06-24T20:15:00Z",
  "fecha_fin_mantenimiento": "2026-06-25T02:00:00Z",
  "creado_en": "2026-06-24T18:35:10Z",
  "actualizado_en": "2026-06-25T02:05:00Z",
  "version": 2
}

```