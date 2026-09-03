# 🥈 Especificación de Modelado Dimensional y Segmentación en Capa Silver

---

## 📌 1. Objetivo y Contexto

En el proceso de evolución de la arquitectura Medallón (**Bronze ➔ Silver ➔ Gold**), la capa **Silver (Plata)** representa el punto de limpieza, tipado, normalización y deduplicación de los datos contables crudos.

Antes de saltar a la capa **Gold** (donde se generan los Datamarts finales y la capa semántica para análisis con LLM), la capa Silver se encargará de **segmentar el dataset único desnormalizado de Bronze en 3 Datasets o Tablas Relacionales/Dimensionales**, garantizando:
1. **Idempotencia y Cero Duplicidad:** Llaves primarias (`PK`) e identidad única por registro.
2. **Normalización (Relación 1 a N):** Reducción de redundancia de texto (ej. nombres de usuarios repetidos miles de veces).
3. **Pistas de Auditoría y Control Interno:** Preservación de trazabilidad de `creado_por` vs `aprobado_por`.

---

## 📐 2. Modelo de Datos Dimensional (Esquema Estrella en Silver)

En lugar de generar un solo archivo monolítico `silver.parquet`, la capa Silver generará **3 archivos Parquet independientes y optimizados**:

```
                       ┌──────────────────────────────────────────┐
                       │               dim_usuarios               │
                       ├──────────────────────────────────────────┤
                       │ PK: user_id                              │
                       │     nombre_usuario                       │
                       │     rol_departamento                     │
                       └────────────────────┬─────────────────────┘
                                            │
                                            │ (1)
                                            │
                      creado_por_user_id    │  aprobado_por_user_id
                      ┌─────────────────────┼─────────────────────┐
                      │ (N)                 │                     │ (N)
                      ▼                     │                     ▼
┌───────────────────────────────────────────┴───────────────────────────────────────────┐
│                                 fact_asientos_contables                               │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ PK: asiento_id               (UUID / Hash MD5 único por movimiento)                   │
│ FK: creado_por_user_id       (Referencia a dim_usuarios.user_id)                      │
│ FK: aprobado_por_user_id     (Referencia a dim_usuarios.user_id)                      │
│ FK: cuenta_id                (Referencia a dim_cuentas.cuenta_id)                     │
│     fecha_asiento            (TIMESTAMP)                                              │
│     monto_debe               (DOUBLE)                                                 │
│     monto_haber              (DOUBLE)                                                 │
│     monto_neto               (DOUBLE)                                                 │
│     entidad                  (VARCHAR - Entidad/Tercero contable)                     │
│     descripcion_nota         (VARCHAR - Observación o concepto del asiento)           │
└───────────────────────────────────────────────────▲───────────────────────────────────┘
                                                    │ (N)
                                                    │
                                                    │ (1)
                                       ┌────────────┴─────────────┐
                                       │       dim_cuentas        │
                                       ├──────────────────────────┤
                                       │ PK: cuenta_id            │
                                       │     codigo_cuenta        │
                                       │     nombre_cuenta        │
                                       │     centro_costo_id      │
                                       └──────────────────────────┘
```

---

## 📊 3. Especificación de Datasets (Capas de Salida en Parquet)

### 3.1. `dim_usuarios.parquet` (Dimensión de Usuarios y Auditores)
- **Propósito:** Almacenar la entidad única de usuarios del sistema (ej. 19 usuarios identificados).
- **Esquema:**
  - `user_id` (INT / STRING, PK): Identificador único del usuario.
  - `nombre_usuario` (VARCHAR): Nombre completo o username.
  - `rol_departamento` (VARCHAR): Rol contable o área de pertenencia.

### 3.2. `dim_cuentas.parquet` (Dimensión de Cuentas y Centros de Costo)
- **Propósito:** Catalogar el plan de cuentas y la estructura organizacional.
- **Esquema:**
  - `cuenta_id` (INT / STRING, PK): Identificador único de la cuenta.
  - `codigo_cuenta` (VARCHAR): Código PUC / General Ledger (ej. `5105`, `1105`).
  - `nombre_cuenta` (VARCHAR): Nombre descriptivo de la cuenta.
  - `centro_costo_id` (VARCHAR): Centro de costos asignado.

### 3.3. `fact_asientos_contables.parquet` (Tabla de Hechos de Asientos Contables)
- **Propósito:** Registrar los movimientos financieros individuales, montos de dinero y metadatos de auditoría.
- **Esquema:**
  - `asiento_id` (STRING, PK): Llave primaria compuesta o Hash MD5 inmutable.
  - `creado_por_user_id` (FK): Usuario que registró la transacción.
  - `aprobado_por_user_id` (FK): Usuario que aprobó o contabilizó el asiento.
  - `cuenta_id` (FK): Llave foránea hacia `dim_cuentas`.
  - `entidad` (VARCHAR): Entidad bancaria, proveedor o cliente asociado.
  - `fecha_asiento` (TIMESTAMP): Fecha y hora del registro.
  - `monto_debe` (DOUBLE): Débito contable (Entrada/Carga).
  - `monto_haber` (DOUBLE): Crédito contable (Salida/Abono).
  - `monto_neto` (DOUBLE): `monto_debe - monto_haber`.
  - `descripcion_nota` (VARCHAR): Texto explicativo del asiento.

---

## 🛡️ 4. Casos de Uso Preparados para la Capa Gold y Auditoría con LLM

La estructura dimensional creada en **Silver** habilita consultas analíticas inmediatas y ultrarápidas en la capa **Gold** mediante DuckDB:

1. **Riesgo de Control Interno (Segregación de Funciones):**
   ```sql
   -- Asientos donde el creador es el mismo aprobador:
   SELECT f.asiento_id, u.nombre_usuario, f.monto_neto, f.descripcion_nota
   FROM fact_asientos_contables f
   JOIN dim_usuarios u ON f.creado_por_user_id = u.user_id
   WHERE f.creado_por_user_id = f.aprobado_por_user_id;
   ```

2. **Análisis de Calidad de Descripciones (Entrada para el LLM):**
   ```sql
   -- Filtrar asientos con descripciones genéricas o potencialmente vagas:
   SELECT f.asiento_id, f.descripcion_nota, f.monto_neto
   FROM fact_asientos_contables f
   WHERE LENGTH(TRIM(f.descripcion_nota)) < 5 
      OR LOWER(f.descripcion_nota) IN ('varios', 'ajuste', 'ok', 'gastos');
   ```

3. **Flujo Efectivo de Dinero (Cash Flow):**
   - Agregaciones directas de `monto_debe` vs `monto_haber` agrupados por `entidad` y `centro_costo_id`.

---

## 🔄 5. Próximos Pasos para la Implementación
1. Implementar el generador de la dimensión `dim_usuarios` y `dim_cuentas` dentro de `backend/src/silver/domain/pipeline.py` y `silver_service.py`.
2. Garantizar la generación de los 3 archivos Parquet en el directorio del proyecto:
   - `data/projects/<slug>/silver/dim_usuarios.parquet`
   - `data/projects/<slug>/silver/dim_cuentas.parquet`
   - `data/projects/<slug>/silver/fact_asientos.parquet`
