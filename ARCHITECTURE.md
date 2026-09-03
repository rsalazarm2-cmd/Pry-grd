# 🏛️ MAPA DE ARQUITECTURA DEL SISTEMA MEDALLION DE AUDITORÍA FORENSE
### Especificación Visual, Árbol de Carpetas Físico y Topología End-to-End de Módulos
**Proyecto de Maestría en Analítica de Datos | Stack: DuckDB C++, Python Django REST Ninja, Vue 3 + TypeScript**

---

## ⚡ 0. REQUISITO OBLIGATORIO: Instalación del Gestor de Paquetes `uv`

Este proyecto utiliza **`uv`** (Astral Python Package Manager) como gestor único y estricto de dependencias en el Backend. `uv` reemplaza a `pip` y `virtualenv`, garantizando entornos reproducibles en menos de 1 segundo.

### 📥 Instalación de `uv`:

- **Linux / macOS:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Windows (PowerShell):**
  ```powershell
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **Con pip (si ya tienes Python):**
  ```bash
  pip install uv
  ```

### 🚀 Inicialización del Backend con `uv`:
```bash
cd backend
uv sync                           # Sincroniza el entorno virtual .venv e instala dependencias exactas
.venv/bin/python manage.py runserver 8000
```

---

## 🖼️ 1. MAPA VISUAL GRAFICO DE ARQUITECTURA

![Mapa Visual de Arquitectura del Sistema Medallion](/home/rsalazar/Python/Pry_Grd/docs/architecture/assets/system_architecture_map.png)

---

## 🌳 2. ÁRBOL COMPLETO DE CARPETAS Y ESTRUCTURA DE ARCHIVOS DE LA ARQUITECTURA

```
Pry_Grd/ (Raíz del Proyecto)
│
├── ARCHITECTURE.md                             # Documento Principal de Arquitectura Visual
├── PLAN_MAESTRO_INGENIERIA_DATOS.md            # Plan Maestro General de 5 Fases
├── PLAN_MAESTRO_15_CASOS_DE_USO.md             # Plan Maestro de 15 Casos de Uso Reales
├── PLAN_MAESTRO_SUPERPODERES_AUDITORIA.md      # Plan Maestro de Superpoderes Forenses
│
├── backend/                                    # Core Server (Python 3.14 + Django Ninja + DuckDB)
│   ├── manage.py                               # Runner Django
│   ├── pyproject.toml                          # Configuración de dependencias `uv`
│   ├── config/                                 # Configuración del servidor Django
│   │   ├── settings.py                         # Settings Django (Ninja REST API, CORS)
│   │   ├── urls.py                             # Dispatcher URL principal
│   │   └── wsgi.py
│   │
│   └── src/                                    # Clean Architecture Hexagonal Layers
│       ├── core/                               # Punto de entrada HTTP Ninja API
│       │   ├── views.py                        # NinjaAPI Router Central
│       │   └── urls.py                         # Prefix `/api/`
│       │
│       ├── project/                            # Sub-dominio Gestión de Proyectos
│       │   ├── api/
│       │   │   └── project_router.py           # Endpoints CRUD de proyectos reales
│       │   ├── application/                    # Casos de Uso (List, Create, Delete)
│       │   │   ├── list_projects_use_case.py
│       │   │   ├── create_project_use_case.py
│       │   │   ├── delete_project_use_case.py
│       │   │   └── clear_project_data_use_case.py
│       │   ├── domain/
│       │   │   ├── project.py                  # DTOs ProjectDTO, RecipeDTO
│       │   │   └── project_repository.py       # Interfaz ABC
│       │   └── infrastructure/
│       │       └── duckdb_project_repository.py # Repositorio en disco `data/projects/`
│       │
│       ├── bronze/                             # Sub-dominio Capa Bronce (Data Lake Crudo)
│       │   ├── api/
│       │   │   └── bronze_router.py            # Endpoints Profile, Records, Upload, Suggest
│       │   ├── application/
│       │   │   ├── profile_dataset_use_case.py
│       │   │   ├── ingest_bronze_use_case.py
│       │   │   └── suggest_mapping_use_case.py
│       │   ├── domain/
│       │   │   ├── chain_of_custody.py         # Firma SHA-256 de Custodia Digital
│       │   │   └── rules.py
│       │   └── infrastructure/
│       │       ├── bronze_service.py           # Fachada DuckDB Bronce
│       │       ├── bronze_profiler.py          # Profilado SQL vectorizado nulos/min/max/sum
│       │       ├── mapping_rules_persistence_service.py # Memoria JSON (1 ms)
│       │       └── profile_cache_service.py    # Caché SHA-256
│       │
│       ├── silver/                             # Sub-dominio Capa Plata (Data Estandarizada)
│       │   ├── api/
│       │   │   └── silver_router.py            # Endpoints Profile, Transform, Records
│       │   ├── application/
│       │   │   ├── transform_silver_use_case.py
│       │   │   └── query_silver_records_use_case.py
│       │   ├── domain/
│       │   │   ├── source_risk_classifier.py
│       │   │   └── atomicity.py
│       │   └── infrastructure/
│       │       ├── silver_service.py           # Compilador AST & Queries Plata
│       │       ├── silver_quality_profiler.py  # Calculador de KPIs Financieros ($) en 33 campos
│       │       └── duckdb_silver_query_builder.py
│       │
│       ├── gold/                               # Sub-dominio Capa Oro (Data Marts & Stats)
│       │   ├── api/
│       │   │   └── gold_router.py              # Endpoints Pearson, Spearman, Z-Score
│       │   ├── application/
│       │   │   ├── query_gold_balances_use_case.py
│       │   │   └── query_gold_account_balances_use_case.py
│       │   └── infrastructure/
│       │       └── gold_service.py             # Agregaciones de Balances y Saldos
│       │
│       └── shared/                             # Módulos y Dominio Compartido
│           ├── domain/
│           │   ├── journal_entry.py            # DTOs Pydantic V2 de Dominio
│           │   └── journal_entry_repository.py # Interface ABC
│           └── infrastructure/
│               ├── engine.py                   # DuckDBEngine Pool Singleton (C++)
│               ├── duckdb_journal_repository.py
│               └── storage/
│                   └── atomic_parquet_writer.py # Escritor Atómico Parquet (.tmp ➔ replace)
│
├── frontend/                                   # Client Web (Vue 3 + TypeScript Strict)
│   ├── index.html
│   ├── vite.config.ts                          # Configuración Vite Proxy `/api` ➔ `localhost:8000`
│   ├── package.json
│   └── src/
│       ├── main.ts                             # Mount App Vue 3 & Pinia
│       ├── App.vue                             # Root Layout & Smart Navigation
│       ├── api/                                # Clientes REST API (Fetch Wrapper)
│       │   ├── http_client.ts                  # Fetch base con prefijo `/api`
│       │   ├── projects_api.ts                 # CRUD Proyectos
│       │   ├── bronze_api.ts                   # Ingesta & Profiling Bronce
│       │   └── silver_api.ts                   # Registros & AST Plata
│       ├── components/                         # Componentes Reutilizables
│       │   ├── layout/
│       │   │   ├── AppHeader.vue               # Encabezado Enterprise & Menú Button
│       │   │   └── NavDrawer.vue               # Menú Hamburguesa con Proyectos Reales & Modal Delete
│       │   ├── modals/
│       │   │   └── UploadDatasetModal.vue      # Dropzone CSV/Parquet
│       │   ├── diagnostics/
│       │   │   └── ProfilingPanel.vue          # Tablero de EDA & Nulos
│       │   ├── tables/
│       │   │   └── DataTable.vue               # Grilla Paginada de Datos
│       │   └── forms/
│       │       └── ColumnMappingTable.vue      # Constructor de Mapeo Semántico
│       ├── composables/                        # Vue Composition API Hooks
│       │   ├── useBronzeProfile.ts
│       │   ├── useBronzeRecords.ts
│       │   ├── useSilverRecords.ts
│       │   └── useSilverTransform.ts
│       ├── stores/                             # Pinia State Stores
│       │   ├── project_store.ts                # Estado de Proyectos Reales & Auto-Nav
│       │   └── ui_store.ts                     # Estado de Pestañas Activas
│       └── views/                              # Páginas / Workspaces por Capa
│           ├── BronzeWorkspace.vue             # Workspace Capa Bronce
│           ├── SilverWorkspace.vue             # Workspace Capa Plata
│           ├── GoldWorkspace.vue               # Workspace Capa Oro
│           └── AuditWorkspace.vue              # Command Center SOX
│
├── docs/                                       # Suite Completa de Documentación
│   ├── architecture/                           # 10 Archivos Técnicos de Arquitectura
│   │   ├── 01_ARQUITECTURA_GENERAL_MEDALLION.md
│   │   ├── 02_DESEMPEÑO_PC_ESCRITORIO_OPTIMIZACION.md
│   │   ├── 03_INTEGRACION_MOTOR_RUST.md
│   │   ├── 04_CAPA_BRONCE_DATA_LAKE_EDA.md
│   │   ├── 05_CAPA_PLATA_ESTANDARIZACION_AST_LINEAJE.md
│   │   ├── 06_CAPA_ORO_MODELOS_ESTADISTICOS_PEARSON.md
│   │   ├── 07_COMMAND_CENTER_AUDITORIA_SOX_FORENSE.md
│   │   ├── 08_MODELO_DE_DATOS_CANONICO_33_CAMPOS.md
│   │   ├── 09_MAPA_DE_COMPONENTES_BACKEND_FRONTEND.md
│   │   ├── 10_GUIA_DESARROLLO_RESTRICCIONES_ORO.md
│   │   └── assets/
│   │       └── system_architecture_map.png     # Infografía de Arquitectura Visual
│   └── plans/                                  # 5 Planes de Implementación Autónomos
│       ├── FASE_1_MOTOR_EXPRESIONES_FECHAS.md
│       ├── FASE_2_CANVAS_VISUAL_ESQUEMA_PLATA.md
│       ├── FASE_3_LINEAJE_Y_PERSISTENCIA.md
│       ├── FASE_4_ESTADISTICA_PEARSON_SPEARMAN_ORO.md
│       └── FASE_5_COMMAND_CENTER_SOX.md
│
└── data/                                       # Storage Físico Local en Disco
    └── projects/                               # Isolación de Datos por Proyecto
        └── {project_id}/
            ├── bronze/
            │   └── bronze.parquet              # Data Lake Crudo Original
            ├── silver/
            │   └── silver.parquet              # Data Estandarizada 33 Campos
            ├── .column_mapping_rules.json      # Memoria Inmutable del Auditor (1 ms)
            ├── .profile_cache.json             # Caché SHA-256
            └── recipe.json                     # Receta de Transformación
```

---

## 📌 3. RESUMEN DE CAPAS MEDALLION

### 🥉 Capa Bronce (Data Lake Crudo)
- **Componentes:** Ingesta Parquet Atómica (`atomic_parquet_writer.py`), Firma SHA-256 de Custodia Digital e Inmutabilidad, Profilado Estadístico Físico Vectorizado en DuckDB (`bronze_profiler.py`).

### 🥈 Capa Plata (Data Estandarizada, Reducida y Limpia)
- **Componentes:** Schema Canvas Interactivo, Express AST Engine de Fechas (`DATEDIFF`, días de semana, coincidencia % match), Amount Splitter Engine (+/- ➔ Cargo/Abono), Ley de Benford (MAD), Entropía de Shannon ($H(X)$), Linaje Transparente y Memoria Inmutable `.column_mapping_rules.json` (1 ms).

### 🥇 Capa Oro (Data Marts & Modelado Estadístico Avanzado)
- **Componentes:** Matrices de Correlación de Pearson ($r$) y Spearman ($\rho$), Distancia Multivariada de Mahalanobis ($D^2$), Serie de Tiempo Z-Score de Fechas Atípicas ($Z_t \ge 2.5$), Comparativa Paramétrica (Tukey IQR) y Command Center SOX con impacto financiero ($).
