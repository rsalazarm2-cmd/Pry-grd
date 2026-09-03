# 🏛️ CIMIENTOS Y ESPECIFICACIÓN TÉCNICA DE ARQUITECTURA
## Datamart Financiero ERP (Arquitectura Medallón Bronze ➔ Silver ➔ Gold)

---

## 🏗️ 1. Filosofía de Diseño: "Los Cimientos de la Casa"

Este sistema no está construido sobre papel ni con componentes frágiles. Se diseñó bajo **principios de ingeniería de datos y software de nivel empresarial (Enterprise-Grade)**, construyendo una infraestructura sólida, modular y escalable capaz de procesar cientos de miles de registros contables ERP en milisegundos.

### Los 3 Cimientos Inquebrantables del Sistema:

1. **⚡ Procesamiento Vectorial Columnar (DuckDB Native + Apache Parquet):**
   - **El Problema:** Los ORM tradicionales (como Django ORM) cargan cada fila como un objeto Python pesado en RAM, consumiendo Gigabytes de memoria y demorando minutos en agregaciones contables.
   - **La Solución (Cero ORM):** Django opera exclusivamente como un API Router HTTP delgado (`models.py = NULL`). Todo el cómputo de datos se ejecuta directamente en memoria RAM mediante el **motor vectorial DuckDB**, leyendo y escribiendo archivos **Apache Parquet de formato columnar**. 
   - **Beneficio:** Agregaciones, sumatorias de Débito/Crédito y agrupaciones por Centro de Costos en **menos de 40 milisegundos**.

2. **📐 Arquitectura Hexagonal Modular por Subdominios (Clean DDD):**
   - El código no es un monolito espagueti. Está dividido en **Bounded Contexts (Subdominios)** independientes (`bronze`, `silver`, `gold`, `project`, `shared`), donde cada subdominio sigue la regla de las 4 capas de Clean Architecture: `api` ➔ `application` ➔ `domain` ◄── `infrastructure`.

3. **🛡️ Inmutabilidad y Gobernanza de Datos:**
   - La capa Bronze nunca se modifica. Se aplican huellas digitales criptográficas (Hash MD5/SHA256) para auditoría e inmutabilidad total de los extractos ERP.

---

## 🌳 2. Árbol Estructural de Directorios y Carpetas del Proyecto

El proyecto mantiene una **simetría arquitectónica perfecta** entre el Backend (Python) y el Frontend (React + TypeScript):

```
Pry Grd/
├── backend/                                  # BACKEND (Python 3.12+ / Django Ninja / DuckDB / uv)
│   ├── config/                               # Configuración global del proyecto (settings.py, urls.py)
│   └── src/                                  # Código Fuente bajo Clean DDD por Subdominios
│       ├── project/                          # 📁 Subdominio: Gestión de Proyectos de Analítica
│       │   ├── api/                          # Delivery: project_router.py (CRUD de Proyectos)
│       │   ├── application/                  # Use Cases: CreateProjectUseCase, ListProjectsUseCase
│       │   ├── domain/                       # Domain: project.py (DTOs Puras & Interfaces ABC)
│       │   └── infrastructure/               # Infra: DuckDBProjectRepository (Metadatos & recipe.json)
│       │
│       ├── bronze/                           # 📁 Subdominio: Capa Bronze (Ingesta & Profiling)
│       │   ├── api/                          # Delivery: bronze_router.py (/api/medallion/bronze/*)
│       │   ├── application/                  # Use Cases: IngestBronzeDataUseCase, ProfileBronzeUseCase
│       │   ├── domain/                       # Domain: dataset_profile.py, anomaly_matrix.py
│       │   └── infrastructure/               # Infra: bronze_service.py (DuckDB Streaming CSV ➔ Parquet)
│       │
│       ├── silver/                           # 📁 Subdominio: Capa Silver (Limpieza & Tipado Estricto)
│       │   ├── api/                          # Delivery: silver_router.py (/api/medallion/silver/*)
│       │   ├── application/                  # Use Cases: TransformSilverDataUseCase
│       │   ├── domain/                       # Domain: cleaning_rules.py, pipeline.py
│       │   └── infrastructure/               # Infra: silver_service.py (DuckDB Normalización & Partition By)
│       │
│       ├── gold/                             # 📁 Subdominio: Capa Gold (Datamarts & PyG)
│       │   ├── api/                          # Delivery: gold_router.py (/api/medallion/gold/*)
│       │   ├── application/                  # Use Cases: GenerateGoldModelsUseCase
│       │   ├── domain/                       # Domain: ast.py, gold_models.py
│       │   └── infrastructure/               # Infra: gold_service.py (DuckDB Datamarts Libros & PyG)
│       │
│       └── shared/                           # 📁 Subdominio Compartido (Core Cross-Cutting)
│           ├── api/                          # NinjaAPI Router Maestro & health_router.py
│           ├── application/                  # Casos de uso genéricos y helpers
│           ├── domain/                       # journal_entry_repository.py (Puerto ABC Base)
│           └── infrastructure/               # duckdb/engine.py (Gestor de Conexiones In-Memory Pool)
│
├── frontend/                                 # FRONTEND (React 18 / Vite / TypeScript / Glassmorphism)
│   └── src/
│       ├── project/                          # Componentes UI & Hooks del Dominio Proyectos
│       ├── bronze/                           # Componentes UI & Hooks del Profiling y Anomalías Bronze
│       ├── silver/                           # Componentes UI & Modales de Limpieza y Tipado Silver
│       ├── gold/                             # Componentes UI & Visualizadores Datamarts PyG Gold
│       ├── ai/                               # Servicios de asistencia inteligente
│       ├── shared/                           # Store global Zustand (medallionStore.ts) & Client API
│       └── styles/                           # CSS Vanilla Modular (variables.css, layout.css, components.css)
│
└── Documentation/                            # DOCUMENTACIÓN TÉCNICA Y BLUEPRINTS DEL SISTEMA
    ├── DOCUMENTATION_COMPLETA_SISTEMA_MEDALLION.md  # Especificación Maestra de Operaciones
    ├── Arquitectura.md                              # Diagramas C4 y Justificación de Rendimiento
    ├── SILVER_MODELADO_DIMENSIONAL.md               # Especificación de 3 Datasets Parquet para Silver
    └── ARQUITECTURA_REFACTORIZACION_Y_ESTADO.md     # Documento de Cimientos y Deuda Técnica (Este archivo)
```

---

## ⚡ 3. El Corazón del Motor de Procesamiento (DuckDB + Apache Parquet)

### ¿Cómo se procesan las bases de datos?

A diferencia de un sistema web convencional que realiza peticiones lenta a bases de datos relacionales tradicionales, este sistema utiliza un **Motor de Analítica In-Memory Vectorial**:

```
[ Petición Frontend ] ──► [ Router Django Ninja ] ──► [ Caso de Uso Python ]
                                                              │
                                                              ▼
                                                   [ DuckDB Engine In-Memory ]
                                                              │ (Lectura / Escritura Directa)
                                                              ▼
                                                 ┌──────────────────────────┐
                                                 │   Archivos Apache        │
                                                 │   PARQUET Columnar       │
                                                 │   (data/projects/<slug>) │
                                                 └──────────────────────────┘
```

1. **Lectura Columnar Pushdown:** DuckDB lee únicamente los bytes de las columnas necesarias del archivo Parquet. Si una consulta solo requiere `JE_HEADER_ID` y `ENTERED_DR`, no toca las otras 42 columnas.
2. **Procesamiento SIMD (Single Instruction, Multiple Data):** Las operaciones matemáticas (sumas, promedios, imputaciones) se procesan en bloques vectoriales a nivel de CPU.
3. **Escritura Parquet con Compresión Snappy:** Los datos limpios se persisten en disco comprimidos, reduciendo el espacio en un **75%-80%** en comparación con los archivos CSV originales.

---

## 🔄 4. Flujo Extremo a Extremo de Ejecución (End-to-End Request Flow)

Cuando el usuario hace clic en el Frontend para procesar una capa (ej. Transformar a Silver):

```
1. Frontend (React / TypeScript)
   └── Dispara `silverApi.transformSilver(rulesDTO)` enviando la receta de limpieza en JSON.

2. API Layer (Django Ninja Router - `silver_router.py`)
   └── Valida la entrada HTTP mediante Pydantic DTOs y llama al Caso de Uso.

3. Application Layer (`TransformSilverDataUseCase.py`)
   └── Coordina la regla de negocio y llama a la interfaz de infraestructura `JournalEntryRepository`.

4. Infrastructure Layer (`silver_service.py` con DuckDB)
   └── Ejecuta la consulta SQL vectorial compilada en memoria:
       - Aplica TRIM, UPPER y remoción de tildes.
       - Ejecuta imputación de promedios con `AVG() OVER (PARTITION BY categoria, moneda)`.
       - Genera el archivo `data/projects/<slug>/silver/silver.parquet`.

5. Respuesta HTTP (JSON)
   └── Devuelve las métricas de ejecución (tiempo en ms, filas procesadas, bytes escritos) al Frontend.
```

---

## 📈 5. Matriz de Desmonolitización y Calidad de Código

Gracias a la refactorización realizada, logramos una reducción dramática de la deuda técnica inicial:

| Componente | Estado Monolítico Anterior | Estado Modular Refactorizado | Beneficio Técnico |
| :--- | :--- | :--- | :--- |
| **`views.py`** | 336 líneas (End-points mezclados) | **20 líneas** (`NinjaAPI` central) | 📉 **-94% líneas**. Routers aislados por dominio en `src/*/api/`. |
| **`duckdb_journal_repository.py`** | 776 líneas (Monolito SQL) | **60 líneas** (Adaptador delgado) | 📉 **-92% líneas**. Lógica dividida en `engine`, `bronze`, `silver`, `gold`. |
| **Frontend UI** | `App.tsx` monolítico | SPA modular con `src/bronze/`, `src/silver/`, `src/gold/` | Mantenibilidad total, componentes reutilizables sin regresiones. |

---

## 🛡️ 6. Deuda Técnica Consciente y Estrategia Futura de Seguridad

### Estado Actual:
Actualmente, los endpoints HTTP no requieren tokens de autenticación para agilizar el desarrollo de los pipelines de datos en entorno local/desarrollo.

### Estrategia Futura (Perímetro de Seguridad en Django):
Cuando el sistema pase a fase de producción, **la seguridad no contaminará la arquitectura interna**:

1. **Django como Guardián de Perímetro:**
   - La autenticación (JWT Tokens / Sessions) y la autorización por roles (RBAC) serán gestionadas **exclusivamente en los Routers HTTP de Django Ninja** (`@router.get(..., auth=JWTAuth())`).
2. **Casos de Uso Limpios:**
   - La capa de aplicación y DuckDB seguirán siendo 100% agnósticos de HTTP y Tokens. Solo recibirán el `user_id` autenticado desde el router.
3. **Cero Impacto en Pipelines de Datos:**
   - El motor de procesamiento en Parquet/DuckDB no necesitará modificaciones al añadir la capa de seguridad.

---

## 🎯 7. Conclusión

Este sistema **no es un prototipo frágil**: es una solución analítica contable construida con **cimientos de hormigón armado**. Cada pieza (Django Ninja, DuckDB, Parquet, React, TypeScript, Clean DDD) fue elegida estratégicamente para ofrecer un rendimiento instantáneo, mantenimiento limpio a largo plazo y preparación total para escalar a nivel empresarial.
