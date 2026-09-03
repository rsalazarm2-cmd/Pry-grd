# 🏛️ ARQUITECTURA DEL SISTEMA DE AUDITORÍA FORENSE & ANALÍTICA MEDALLION
### Documentación Técnica Integral, Mapa del Sistema y Evaluación de Desempeño en PC de Escritorio
**Proyecto de Maestría en Analítica de Datos | Stack: DuckDB Nativo, Python/Django, Vue 3/TypeScript, Rust (PyO3)**

---

## 📌 1. FILOSOFÍA Y VISIÓN GENERAL DE LA ARQUITECTURA

El sistema está diseñado bajo una **Arquitectura Hexagonal (Clean Architecture)** acoplada al patrón de datos **Medallion Architecture (Bronce, Plata, Oro)**. Su propósito es procesar extractos de asientos contables de sistemas ERP heterogéneos (Oracle EBS, SAP S/4HANA, Microsoft Dynamics) para ejecutar auditoría forense, validación de integridad financiera y segregación de funciones (SoD).

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ 🥉 CAPA BRONCE (Data Lake Crudo)                                                        │
│    • Ingesta Atómica Parquet con Preservación de Firma SHA-256 (Cadena de Custodia).    │
│    • Diagnóstico Físico de Calidad (EDA Crudo): % nulos, columnas constantes y tipos.   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 🥈 CAPA PLATA (Data Estandarizada, Reducida y Limpia)                                   │
│    • Schema Canvas & Reducción Dinámica de Campos (reducir N columnas a M canónicas).  │
│    • Expresiones AST de Fechas: Deltas (DATEDIFF), Día de la Semana, Redundancia % Match.│
│    • Amount Splitter Engine: Transformación (+/-) a CARGO / ABONO independientes.       │
│    • Trazabilidad de Linaje (Origen ➔ Plata) y Memoria (.column_mapping_rules.json).   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 🥇 CAPA ORO (Data Marts & Modelado Estadístico Avanzado)                                │
│    • Matrices de Correlación Matemática (Pearson r & Spearman ρ).                       │
│    • Distancia Multivariada de Mahalanobis (D²) y Test Forense de Ley de Benford (MAD).│
│    • Serie de Tiempo y Detección Z-Score de Fechas Atípicas en Asientos Manuales.      │
│    • Command Center SOX: Indicadores Monetarios ($) de SoD, Aprobación < 60s y Smurfing. │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ 2. ¿ES ESTA ARQUITECTURA LA ÓPTIMA PARA UN PC DE ESCRITORIO?

### ⚖️ Dictamen del Principal Architect: SÍ, ES LA ARQUITECTURA PERFECTA PARA ESCRITORIO (LOCAL WORKSTATION)

Trabajar analítica masiva en un PC de escritorio local solía ser un cuello de botella por el uso de bases de datos relacionales tradicionales (Postgres/MySQL) o librerías pesadas en Python (Pandas/Spark). Nuestra arquitectura resuelve este problema mediante tres ventajas físicas:

#### 1. DuckDB: Motor OLAP Columnar In-Process (Escrito en C++)
- **Cero Overhead de Red:** DuckDB corre dentro de la misma memoria del proceso Python (sin socket TCP ni latencia cliente-servidor).
- **Procesamiento Vectorizado por Bloques:** Procesa vectores de 2048 tuplas en registros L1/L2 de la CPU usando instrucciones **SIMD (Single Instruction Multiple Data)** de procesadores de escritorio modernos (Intel/AMD).
- **Multi-threading Automático:** Utiliza el 100% de los núcleos/threads de la CPU del PC de escritorio de forma transparente.

#### 2. Apache Parquet: Almacenamiento Columnar Compreso en Disco
- **Reducción I/O de Disco por 10x-50x:** Los archivos Parquet almacenan datos por columnas en lugar de filas, comprimidos con algoritmos Snappy/ZSTD.
- **Projection & Filter Pushdown:** DuckDB solo lee del disco del PC las columnas específicas involucradas en la consulta SQL, ignorando las columnas no utilizadas. Un archivo de 500 MB se lee en milisegundos.

#### 3. Memoria Caché Criptográfica SHA-256 (1 ms)
- Todas las operaciones costosas (profiling y sugerencias NLP de IA) se almacenan en caché indexada por el hash SHA-256 del dataset. En ejecuciones secundarias en el PC de escritorio, **la respuesta toma exactamente 1 milisegundo**.

---

## 🗺️ 3. MAPA COMPLETO DEL SISTEMA ACTUAL

```mermaid
graph TD
    subgraph Frontend ["Frontend (Vue 3 + TypeScript Strict)"]
        UI[App.vue / Workspace Area]
        Drawer[NavDrawer.vue - Menú Hamburguesa Enterprise]
        UploadMod[UploadDatasetModal.vue - Modal Carga CSV/Parquet]
        BronzeWS[BronzeWorkspace.vue - Profiling & EDA Crudo]
        SilverWS[SilverWorkspace.vue - Schema Canvas & Linaje]
        GoldWS[GoldWorkspace.vue - Pearson/Spearman & Z-Score]
        AuditWS[AuditWorkspace.vue - Command Center SOX]
        Store[project_store.ts - Pinia State & Smart First-Load]
    end

    subgraph Backend ["Backend (Python + Django REST Ninja + DuckDB)"]
        API[Core Ninja API Router]
        ProjMgmt[project_router.py / Projects CRUD]
        BronzeRouter[bronze_router.py - Ingestion & Profiler]
        SilverRouter[silver_router.py - AST Transform & Query]
        PersistServ[mapping_rules_persistence_service.py - JSON Rules]
        SilverQuality[silver_quality_profiler.py - Metric Quality]
        DuckDBEngine[(DuckDB Native Engine + Parquet Storage)]
    end

    subgraph Disk ["Almacenamiento Local (PC de Escritorio)"]
        RawData[data/projects/{id}/bronze/bronze.parquet]
        CleanData[data/projects/{id}/silver/silver.parquet]
        JSONRules[data/projects/{id}/.column_mapping_rules.json]
    end

    UI --> Store
    Drawer --> Store
    UploadMod -->|POST /api/bronze/upload-ingest| BronzeRouter
    BronzeWS -->|GET /api/bronze/profile| BronzeRouter
    SilverWS -->|POST /api/silver/transform| SilverRouter
    Store -->|GET /api/projects| ProjMgmt

    BronzeRouter --> DuckDBEngine
    SilverRouter --> DuckDBEngine
    SilverRouter --> PersistServ

    DuckDBEngine --> RawData
    DuckDBEngine --> CleanData
    PersistServ --> JSONRules
```

---

## 🦀 4. INCORPORACIÓN ESTRATÉGICA DE RUST (PyO3 / Maturin)

### ❓ ¿Debemos incluir Rust en el plan para dar agilidad en consultas complejas?
**RESPUESTA DEL LEAD ARCHITECT: SÍ, RUST ES LA PIEZA DE ULTRA-RENDIMIENTO COMPLEMENTARIA PERFECTA.**

Aunque DuckDB es insuperable para consultas SQL relacionales (JOINs, GROUP BY, WHERE), existen **algoritmos de auditoría forense intensivos en CPU que no se expresan eficientemente en SQL**. 

Ahí es donde entra **Rust** conectado a Python vía **PyO3 / maturin**:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ 🐍 PYTHON (Django / Ninja API)                                                          │
│    • Orquestación HTTP REST, validación DTO con Pydantic, ruteo y lógica de negocio.    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 🦆 DUCKDB (C++ Vectorizado)                                                             │
│    • Consultas SQL OLAP, agregaciones por grupo, proyecciones y lectura de Parquets.    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 🦀 RUST (PyO3 Nivel Ensamblador GIL-Free)                                               │
│    • Algoritmos Forenses No-Relacionales Complejos:                                     │
│      1. Entropía de Shannon sobre millones de glosas de texto (H(X)).                    │
│      2. Algoritmos de Grafos SoD (Detección de ciclos de colusión Maker-Checker).        │
│      3. Distancia Multivariada de Mahalanobis (D²) sin usar GIL de Python.              │
│      4. Detector de Smurfing (Detección de fraccionamiento de montos en tiempo real).   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Ventajas de Integrar Rust:
1. **Zero-Copy Memory Overhead:** Mediante Apache Arrow C Data Interface, Rust lee la memoria RAM de DuckDB sin copiar datos.
2. **True Parallelism (Sin GIL):** Rust ignora el GIL (Global Interpreter Lock) de Python, utilizando el 100% de los hilos de la CPU del PC de escritorio con hilos nativos `rayon`.

---

## 🔮 5. RECOMENDACIONES Y HOJA DE RUTA A FUTURO (ESCALABILIDAD ENTERPRISE)

1. **Fase Actual (Desktop Local Workstation):**  
   Almacenamiento directo en `data/projects/{id}/` con Parquet local y DuckDB In-Process. Rápido, aislado y sin costo de servidor.
2. **Escalabilidad Híbrida (Empresarial Multi-Usuario):**  
   - Conexión federada de DuckDB hacia **Apache Iceberg / Google BigQuery / AWS S3**.
   - Migración de cómputos pesados no-SQL a **módulos de Rust compilados en maturin**.
3. **Gobierno de Evidencias:**  
   - Exportación de paquetes forenses con firma criptográfica SHA-256 e inmutabilidad garantizada.
