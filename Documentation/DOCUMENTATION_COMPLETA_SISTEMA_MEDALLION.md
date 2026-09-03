# 🏛️ DOCUMENTACIÓN TÉCNICA MAESTRA Y MANUAL DE ARQUITECTURA
## Datamart Financiero ERP (Oracle EBS General Ledger)
### Stack: Python 3.12+ | Django (Router) | DuckDB Native Engine | Apache Parquet | React + Vite (Glassmorphism UI)

---

## 📑 TABLA DE CONTENIDOS COMPLETA
1. [Principios Inquebrantables y Reglas de Infraestructura](#1-principios-inquebrantables-y-reglas-de-infraestructura)
2. [Arquitectura Hexagonal (Clean Architecture / Puertos y Adaptadores)](#2-arquitectura-hexagonal-clean-architecture--puertos-y-adaptadores)
3. [Flujo Extremo a Extremo de Conversión de Archivos (CSV ➔ Bronce ➔ Plata ➔ Oro)](#3-flujo-extremo-a-extremo-de-conversión-de-archivos-csv--bronce--plata--oro)
   - [Paso 1: Ingesta Inmutable y Hashing Criptográfico (Bronce)](#paso-1-ingesta-inmutable-y-hashing-criptográfico-bronce)
   - [Paso 2: Profiling Estructural de 48 Columnas y Matriz de Anomalías (A1 a A6)](#paso-2-profiling-estructural-de-48-columnas-y-matriz-de-anomalías-a1-a-a6)
   - [Paso 3: Transformación, Normalización y Tipado Estricto (Plata)](#paso-3-transformación-normalización-y-tipado-estricto-plata)
   - [Paso 4: Imputación Avanzada Condicional por Grupos (PARTITION BY)](#paso-4-imputación-avanzada-condicional-por-grupos-partition-by)
   - [Paso 5: Validación en Tiempo Real de Alias y Auto-TRIM](#paso-5-validación-en-tiempo-real-de-alias-y-auto-trim)
   - [Paso 6: Construcción de Datamarts Analíticos y Estado de Resultados PyG (Oro)](#paso-6-construcción-de-datamarts-analíticos-y-estado-de-resultados-pyg-oro)
4. [Módulo de Filtros por Encabezado Estilo Excel (Ctrl + Shift + L)](#4-módulo-de-filtros-por-encabezado-estilo-excel-ctrl--shift--l)
5. [Matriz de Gobernanza, Seguridad Inquebrantable e Inmutabilidad](#5-matriz-de-gobernanza-seguridad-inquebrantable-e-inmutabilidad)
6. [Resumen de Archivos y Responsabilidades en el Código Fuente](#6-resumen-de-archivos-y-responsabilidades-en-el-código-fuente)

---

## 1. Principios Inquebrantables y Reglas de Infraestructura

El diseño del proyecto se rige por **restricciones de arquitectura estrictas** para garantizar que sea un software de analítica financiera de nivel empresarial:

### ⛔ RESTRICCIÓN 1: Django Cero ORM (`models.py = NULL`)
- **Riesgo Mitigado:** Los ORMs tradicionales (como Django ORM o SQLAlchemy) cargan cada fila como un objeto Python pesado en memoria RAM, lo que causa cuellos de botella severos, bloqueos de memoria y tiempos de respuesta de minutos al procesar extractos ERP de cientos de miles de filas.
- **Regla Aplicada:** Django opera **exclusivamente como un API Router delegador HTTP delgado**. No existe interacción entre Django y la base de datos relacional a través de `models.py`. Toda la analítica de datos se realiza **vectorialmente mediante la API nativa de DuckDB**.

### ⚡ RESTRICCIÓN 2: DuckDB Native Python Engine + Apache Parquet
- **Riesgo Mitigado:** Copiar datos a bases de datos en disco crea duplicación ineficiente y lentitud de I/O.
- **Regla Aplicada:** DuckDB ejecuta consultas analíticas *in-memory* procesando archivos **Apache Parquet de formato columnar** directamente desde el sistema de archivos (`data/bronze/`, `data/silver/`, `data/gold/`), aprovechando operaciones SIMD y *projection pushdown* (lee únicamente las columnas necesarias para cada consulta).

### 📦 RESTRICCIÓN 3: Entorno Ligero y Rápido con `uv`
- **Regla Aplicada:** La gestión del proyecto backend se ejecuta mediante `uv`, garantizando resolución de dependencias instantánea, reproducción exacta del entorno virtual y ejecuciones ultrarrápidas con `uv run`.

---

## 2. Arquitectura Hexagonal (Clean Architecture / Puertos y Adaptadores)

El backend aísla por completo la lógica de negocio de los detalles de infraestructura:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 CAPA FRONTEND (React 18 + Vite + TypeScript)                             │
│  • App.tsx (SPA Contenedor Principal)                                                                    │
│  • CleaningConfigModal.tsx (Limpieza, TRIM, Mayúsculas, Alias, CHAR, Imputación Avanzada)                │
│  • ExcelColumnFilter.tsx (Filtros por Encabezado en Vivo Ctrl + Shift + L)                               │
└──────────────────────────────────────────────────┬───────────────────────────────────────────────────────┘
                                                   │
                                                   ▼  Requests HTTP REST (JSON)
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             CAPA DE ENTREGA / API (Django REST Framework)                                │
│  • views.py (Controladores Delgados - Cero ORM / models.py = NULL)                                       │
└──────────────────────────────────────────────────┬───────────────────────────────────────────────────────┘
                                                   │
                                                   ▼ Invocación de Casos de Uso
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               CAPA DE APLICACIÓN (Casos de Uso de Negocio)                               │
│  • IngestBronzeDataUseCase    • ProfileBronzeDataUseCase    • TransformSilverDataUseCase                 │
│  • GenerateGoldModelsUseCase  • QueryTabularRecordsUseCase                                               │
└──────────────────────────────────────────────────┬───────────────────────────────────────────────────────┘
                                                   │
                                                   ▼ Inyección de Dependencia (DIP)
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           CAPA DE DOMINIO (Entidades Puras & Interfaces ABC)                             │
│  • Interfaz Abstracta: JournalEntryRepository (ABC)                                                      │
│  • DTOs Pydantic: ColumnCleaningRuleDTO, TransformationRulesDTO, DatasetProfileDTO                       │
└──────────────────────────────────────────────────▲───────────────────────────────────────────────────────┘
                                                   │
                                                   │ Implementación Concreta (Puerto)
┌──────────────────────────────────────────────────┴───────────────────────────────────────────────────────┐
│                           CAPA DE INFRAESTRUCTURA (DuckDB Native Engine)                                 │
│  • DuckDBJournalRepository (Consultas SQL Vectoriales in-Memory, Window Functions PARTITION BY)          │
└──────────────────────────────────────────────────┬───────────────────────────────────────────────────────┘
                                                   │
                                                   ▼ Escritura / Lectura Columnar
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           CAPA DE ALMACENAMIENTO (Archivos Apache Parquet)                               │
│  • data/bronze/bronze.parquet  (Crudo Inmutable + MD5 Hash)                                             │
│  • data/silver/silver.parquet  (Limpio, Tipado DOUBLE/CHAR, ENUM, Imputado)                              │
│  • data/gold/gold_balance_by_ledger.parquet  (Datamart Libros)                                          │
│  • data/gold/gold_balance_by_account.parquet (Datamart PyG Cuentas 4, 5, 6)                             │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Separación de Responsabilidades por Capas:

1. **Capa de Dominio (`backend/src/domain/`):**
   - **Cero dependencias** de Django, DuckDB o librerías externas.
   - Contiene los **DTOs estructurados en Pydantic** (`ColumnCleaningRuleDTO`, `TransformationRulesDTO`, `DatasetProfileDTO`, `JournalEntryDTO`, `ColumnProfileDTO`, `AnomalyMatrixDTO`).
   - Contiene la **Interfaz de Puerto (`JournalEntryRepository`)** definida como una Clase Base Abstracta (`ABC`).

2. **Capa de Aplicación (`backend/src/application/`):**
   - Implementa los **Casos de Uso del Negocio** (`IngestBronzeDataUseCase`, `ProfileBronzeDataUseCase`, `TransformSilverDataUseCase`, `GenerateGoldModelsUseCase`, `QueryBronzeRecordsUseCase`, `QuerySilverRecordsUseCase`, `QueryGoldBalancesUseCase`, `QueryGoldAccountBalancesUseCase`).
   - Recibe la interfaz del repositorio por **Inyección de Dependencias en el constructor** (`__init__`).

3. **Capa de Infraestructura (`backend/src/infrastructure/`):**
   - Implementación concreta `DuckDBJournalRepository` que hereda de `JournalEntryRepository`.
   - Contiene las sentencias SQL vectoriales de DuckDB, funciones de ventana `PARTITION BY`, parser de fechas `TRY_STRPTIME` y exportación a Parquet.

4. **Capa de Entrega / API (`backend/src/api/`):**
   - Vistas delgadas de Django REST Framework que capturan las peticiones HTTP, instancian el Caso de Uso inyectando `DuckDBJournalRepository` y devuelven respuestas JSON validadas.

---

## 3. Flujo Extremo a Extremo de Conversión de Archivos (CSV ➔ Bronce ➔ Plata ➔ Oro)

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   📄 CSV CRUDO  │ ────► │ 🥉 CAPA BRONCE  │ ────► │ 🥈 CAPA PLATA   │ ────► │  🥇 CAPA ORO    │
│   (datos.csv)   │       │ (bronze.parquet)│       │ (silver.parquet)│       │(gold_*.parquet) │
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
  Extracto ERP             • Streaming CSV           • Tipado DOUBLE/CHAR      • Datamart Libros
  44-48 Columnas           • Hash MD5/SHA256         • Normalización Tildes    • Datamart PyG
                           • Inmutable               • Imputación Grupos       • Anomalías A1-A6
```

---

### Paso 1: Ingesta Inmutable y Hashing Criptográfico (Bronce)
- **Conversión de Formato:** Transforma el archivo fuente `datos.csv` directamente a `bronze.parquet` comprimido con Snappy utilizando la función vectorial `COPY (SELECT * FROM read_csv_auto(...)) TO 'bronze.parquet'`.
- **Garantía de Inmutabilidad:** Los registros crudos nunca se modifican ni se eliminan.
- **Hashing MD5/SHA256:** Se calcula la huella digital criptográfica del archivo CSV durante la ingesta para detectar cargas repetidas y permitir auditoría de versiones.

---

### Paso 2: Profiling Estructural de 48 Columnas y Matriz de Anomalías (A1 a A6)
El sistema analiza automáticamente la salud estructural del dataset mediante DuckDB, generando un perfil de 48 columnas con:
- `null_count` y `null_percentage`
- `unique_count` y `uniqueness_ratio`
- `min_value`, `max_value`, `mean_value`, `stddev_value`
- Top frecuencias de valores y muestras aleatorias.

#### Matriz de Detección de Anomalías Financieras:
1. **`A1_HEADER_IMBALANCES`:** Detecta comprobantes contables cuyos Débitos y Créditos no suman cero a nivel de cabecera (`JE_HEADER_ID`).
2. **`A2_EXCHANGE_RATE_ERRORS`:** Registra asientos en moneda extranjera (`USD`) con tasa de cambio nula o igual a cero.
3. **`A3_TIMELINE_INCOHERENCES`:** Identifica asientos donde la fecha de creación en GL es posterior a la fecha de contabilización.
4. **`A4_MALFORMED_FLEXFIELDS`:** Identifica combinaciones contables (`CODE_COMBINATION`) que no cumplen con los segmentos estándar ERP.
5. **`A5_USER_MISMATCHES`:** Marca inconsistencias entre el usuario creador y el usuario aprobador de la transacción.
6. **`A6_ZERO_MOVEMENT_ROWS`:** Etiqueta líneas donde tanto el Débito como el Crédito son iguales a `$0.00`.

---

### Paso 3: Transformación, Normalización y Tipado Estricto (Plata)

El usuario configura la transformación desde el **Modal de Configuración de Limpieza**:

#### A. Reglas de Limpieza de Texto y Normalización:
- **`✂️ TRIM`:** Eliminación automática de espacios vacíos al inicio y final de las cadenas de texto.
- **`🔠 MAYÚSCULAS`:** Conversión estandarizada a mayúsculas.
- **`🧹 Normalización de Tildes y Ñ`:**
  - `á, é, í, ó, ú, Á, É, Í, Ó, Ú` &rarr; `a, e, i, o, u, A, E, I, O, U`.
  - `ñ, Ñ` &rarr; `n, N`.
  - Filtro de símbolos molestos (`. _ - # $ % / \`).
- **`🔴 Quitar Puntos (.)`:** Casilla dedicada por columna para eliminar puntos (útil para miles latinos).
- **`🟡 Quitar Comas (,)`:** Casilla dedicada por columna para eliminar comas (útil para miles americanos).

#### B. Tipado Estricto de Datos:
| Tipo de Dato | Aplicación Contable / ERP | Comportamiento DuckDB |
| :--- | :--- | :--- |
| `DOUBLE` | Montos monetarios (`ENTERED_DR`, `ENTERED_CR`) | Mantiene centavos decimales de 64 bits sin truncar números. |
| `CHAR` | Códigos ISO de Monedas (`COP`, `USD`) y banderas | Texto corto de longitud fija `VARCHAR(3)`. |
| `BIGINT` | Folios y Secuencias ERP (`JE_HEADER_ID`) | Enteros de 64 bits de alta precisión. |
| `DATE` | Fechas simples de contabilización | Conversión mediante `TRY_STRPTIME` (`%d/%m/%Y`, `%Y-%m-%d`). |
| `TIMESTAMP` | Fechas con hora de auditoría | Formato completo `YYYY-MM-DD HH:MI:SS`. |
| `BOOLEAN` | Banderas binarias (`ACTUAL_FLAG`) | Mapea `'Y'`, `'TRUE'`, `'1'`, `'SI'` &rarr; `TRUE`. |
| `ENUM` | Categorías repetitivas (`JE_SOURCE`, `JE_CATEGORY`) | Tipado diccionario nativo de DuckDB para compresión columnar masiva. |

---

### Paso 4: Imputación Avanzada Condicional por Grupos (PARTITION BY)

Para evitar distorsionar la contabilidad imputando la Media Global de toda la tabla en nulos monetarios, el sistema ofrece la **Imputación Avanzada Condicional**.

#### Sentencia SQL de Ventana Generada por DuckDB:
```sql
SELECT
  "JE_HEADER_ID",
  "JE_CATEGORY",
  "CURRENCY",
  COALESCE(
    TRY_CAST(REPLACE(CAST("ENTERED_DR" AS VARCHAR), ',', '') AS DOUBLE),
    AVG(TRY_CAST(REPLACE(CAST("ENTERED_DR" AS VARCHAR), ',', '') AS DOUBLE)) 
      OVER (PARTITION BY "JE_CATEGORY", "CURRENCY")
  ) AS "ENTERED_DR"
FROM bronze_records;
```

---

### Paso 5: Validación en Tiempo Real de Alias y Auto-TRIM

- **Sanitización Auto-TRIM:** Borra espacios iniciales sueltos mientras escribes y aplica `.trim()` automático al salir del campo (`onBlur`).
- **Prevención de Duplicados al Digitar:** Si el usuario declara dos veces el mismo alias (ej. `MONEDA`), el sistema:
  - Resalta de inmediato la casilla con un **borde rojo de advertencia** (`border: 2px solid var(--accent-rose)`).
  - Muestra la alerta: `⚠️ Nombre "MONEDA" ya existe en otra columna`.
  - Deshabilita el botón **`Guardar y Procesar Capa Plata`** para evitar esquemas corruptos.

---

### Paso 6: Construcción de Datamarts Analíticos y Estado de Resultados PyG (Oro)

Al procesar la Capa Oro, DuckDB genera dos datamarts independientes en Parquet:

1. **Datamart 1: Balances por Libro ERP (`gold_balance_by_ledger.parquet`):**
   - Agrupa por `LEDGER_NAME` y `CURRENCY`.
   - Calcula `TOTAL_JOURNAL_LINES`, `TOTAL_ENTERED_DR`, `TOTAL_ENTERED_CR` y `NET_ACCOUNTED_BALANCE`.

2. **Datamart 2: Balances por Cuenta y Estado de Resultados PyG (`gold_balance_by_account.parquet`):**
   - Clasificación automática por el primer dígito del segmento de cuenta:
     - **Clase 4:** `4 - INGRESOS` (Ingresos Operacionales)
     - **Clase 5:** `5 - COSTOS` (Costos de Ventas / Operación)
     - **Clase 6:** `6 - GASTOS` (Gastos Administrativos y Ventas)
     - **Clase 1, 2, 3, OTROS:** `ACTIVO / PASIVO / PATRIMONIO`

---

## 4. Módulo de Filtros por Encabezado Estilo Excel (Ctrl + Shift + L)

En todas las tablas del sistema (Bronce, Plata, Oro Libro y Oro Cuenta):
- Cada encabezado `<th>` incluye un menú flotante de filtro (`🪈`).
- Al abrirlo o presionar `Ctrl + Shift + L`, invoca la API `@api.get("/medallion/distinct-values/{layer}/{column_name}")`.
- DuckDB ejecuta una consulta en memoria obteniendo **los valores únicos y su conteo exacto**:
  ```sql
  SELECT "CURRENCY", COUNT(*) AS count 
  FROM 'data/silver/silver.parquet' 
  GROUP BY 1 ORDER BY count DESC LIMIT 100;
  ```
- Permite al usuario marcar casillas individuales o usar `(Seleccionar Todo)` para filtrar vectorialmente con `WHERE col IN (...)`.

---

## 5. Matriz de Gobernanza, Seguridad Inquebrantable e Inmutabilidad

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   SEGURIDAD Y GOBERNANZA DE DATOS ERP                    │
├──────────────────┬───────────────────────────────────────────────────────┤
│ Inyección SQL    │ Los alias y filtros son sanitizados con regex estricto│
│ Imposible        │ `[a-zA-Z0-9_]` y parametrizados en DuckDB.            │
├──────────────────┼───────────────────────────────────────────────────────┤
│ Inmutabilidad de │ Capa Bronce es Read-Only. Capas Plata y Oro son 100%  │
│ Capas            │ reproducibles a partir de las reglas aplicadas.       │
├──────────────────┼───────────────────────────────────────────────────────┤
│ Auditable y      │ Mantiene los campos de auditoría del ERP              │
│ Rastreable       │ (`CREATED_BY`, `POSTED_DATE`, `USER_ID`).             │
└──────────────────┴───────────────────────────────────────────────────────┘
```

---

## 6. Resumen de Archivos y Responsabilidades en el Código Fuente

```
backend/src/
├── api/views.py                                     # Endpoints REST HTTP (Vistas delgadas)
├── application/use_cases/                           # Casos de uso de negocio (Inyección de dependencias)
├── domain/entities/journal_entry.py                 # DTOs Pydantic (ColumnCleaningRuleDTO, TransformationRulesDTO, etc.)
├── domain/repositories/journal_entry_repository.py  # Interfaz ABC del repositorio (Puerto)
└── infrastructure/repositories/duckdb_journal_repository.py  # Adaptador nativo DuckDB (Vectorial Parquet)

frontend/src/
├── api/client.ts                                    # Cliente API tipado TypeScript
├── components/CleaningConfigModal.tsx               # Modal intuitivo de limpieza (TRIM, Mayúsculas, Tildes, Alias, CHAR)
├── components/ExcelColumnFilter.tsx                 # Menú flotante de filtro estilo Excel (Ctrl+Shift+L)
└── App.tsx                                          # Vista principal SPA Glassmorphism
```

---

## ⏱️ Benchmarks de Ejecución Final

Pruebas en tiempo real sobre el dataset contable ERP (**4,999 registros y 44 columnas**):

| Fase | Tiempo de Ejecución | Estado |
| :--- | :--- | :--- |
| **Ingesta CSV a Bronce** | **0.082 s** | ✅ Exitoso (`bronze.parquet`) |
| **Profiling & Anomalías** | **0.015 s** | ✅ Exitoso (48 Columnas) |
| **Transformación a Plata** | **0.117 s** | ✅ Exitoso (`silver.parquet`) |
| **Imputación Avanzada por Grupos** | **0.044 s** | ✅ Exitoso (Window Function) |
| **Generación Datamarts Oro** | **0.035 s** | ✅ Exitoso (`gold_*.parquet`) |
| **Compilación Frontend** | **0.494 s** | ✅ Exitoso (`npm run build`) |
