# 📊 Matriz Comparativa y Mapeo de Funcionalidades por Capa Medallón
## (Bronze ➔ Silver ➔ Gold) vs. OpenRefine, MS Fabric, Dataprep y Tableau Prep

---

## 📌 1. Resumen Ejecutivo

Este documento evalúa las herramientas de limpieza del mercado (**OpenRefine, Microsoft Fabric, Google Dataprep y Tableau Prep**) y las asigna formalmente dentro de la **Arquitectura Medallón del Sistema (Bronze, Silver, Gold)**.

Aclara con precisión el alcance de cada capa, confirmando la **autodetección transparente en la ingesta (Bronze)**, la **reestructuración profunda en Plata (Silver)** y la analítica final en **Oro (Gold)**.

---

## 🔍 2. Matriz Comparativa General de la Industria

| Funcionalidad / Limpieza | 🥉 Medallion Engine | 🌐 OpenRefine | 🟦 MS Fabric | ☁️ Google Dataprep | 🟠 Tableau Prep | Capa Medallón Asignada |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Autodetección de Delimitador y Encodings** | ✅ **Implementado Nativo** (`read_csv_auto`) | ✅ Sí | ✅ Sí | ✅ Sí | ✅ Sí | 🥉 **BRONZE** (In-Engine) |
| **Hashing Criptográfico (MD5) e Inmutabilidad** | ✅ **Implementado** | ❌ No | ⚠️ Básico | ⚠️ Básico | ❌ No | 🥉 **BRONZE** |
| **Profiling de Salud (Nulos, Unicidad, Min/Max)** | ✅ **Implementado** | ⚠️ Básico | ✅ Sí | ✅ Sí | ✅ Sí | 🥉 **BRONZE** |
| **Detección de Anomalías ERP (A1 a A6)** | ✅ **Especializado** | ❌ No | ❌ No | ❌ No | ❌ No | 🥉 **BRONZE / SILVER** |
| **Descarte de Filas/Basura Vacías al Final** | ✅ **Implementado** (Hacia Silver) | ✅ Sí | ✅ Sí | ✅ Sí | ✅ Sí | 🥈 **SILVER** |
| **Limpieza de Texto (TRIM, UPPER, Tildes, Puntos/Comas)**| ✅ **Implementado** | ✅ Sí | ✅ Sí | ✅ Sí | ✅ Sí | 🥈 **SILVER** |
| **Tipado Estricto (`DOUBLE`, `DATE`, `ENUM`)** | ✅ **Implementado** | ❌ String | ✅ Sí | ✅ Sí | ✅ Sí | 🥈 **SILVER** |
| **Imputación por Grupos (`PARTITION BY`)** | ✅ **Implementado** | ❌ No | ⚠️ Básico | ✅ Sí | ⚠️ LOD | 🥈 **SILVER** |
| **Segmentación Dimensional (3 Datasets `PK`/`FK`)** | ⚠️ **En Reestructuración** | ❌ No | ⚠️ Manual | ⚠️ Manual | ✅ Data Model | 🥈 **SILVER** |
| **Columnas Calculadas (Constructor No-Code)** | ⚠️ *Roadmap* | ✅ GREL | ✅ Custom M | ✅ Derived | ✅ Calculated | 🥈 **SILVER** |
| **VLOOKUP / Enriquecimiento por Llave (Joins)** | ⚠️ *Roadmap* | ✅ Cell.cross | ✅ Merge | ✅ Join step | ✅ Join step | 🥈 **SILVER** |
| **Catálogo de Modelos Matemáticos Financieros** | ⚠️ *Roadmap* | ❌ No | ❌ No | ❌ No | ❌ No | 🥇 **GOLD** |
| **Auditoría Semántica y NLP de Descripciones (LLM)** | ⚠️ *Roadmap* | ❌ No | ❌ No | ❌ No | ❌ No | 🥇 **GOLD** |

---

## 🥉 3. Capa BRONZE (Cobre / Ingesta Transparente e Inspección Cruda)

### 📌 Estado de la Capa Bronze:
Es la capa de ingesta cruda e inmutable. Funciona de manera **transparente y automatizada sin cargar al usuario con configuraciones técnicas innecesarias**.

### ✅ Funcionalidades Totalmente Implementadas en Bronze:
1. **Autodetección Transparente de Delimitador y Codificación (`read_csv_auto`):**  
   DuckDB en el backend detecta automáticamente si el archivo está delimitado por coma (`,`), punto y coma (`;`), tabulador (`\t`) o tubería (`|`), y resuelve el encoding (`UTF-8`, `Latin-1`) sin molestar al usuario en la UI.
2. **Streaming In-Memory (CSV ➔ Parquet):** Conversión directa a `bronze.parquet` in-memory de alta velocidad.
3. **Huella Criptográfica MD5 / SHA256:** Inmutabilidad garantizada y prevención de duplicados vía manifest.
4. **Profiling Estructural de 48 Columnas:** Detección de unicidad, conteo de nulos y estadísticas de distribución.
5. **Matriz de Detección de Anomalías Iniciales (A1-A6):** Identificación de descuadres contables y flexfields malformados.

---

## 🥈 4. Capa SILVER (Plata / Reestructuración, Limpieza y Normalización)

### 📌 Estado de la Capa Silver:
Es la capa donde se transforman y depuran los datos crudos para alcanzar la calidad deseada antes de alimentar los modelos analíticos.

### 🛠️ Reestructuración y Funcionalidades de la Capa Silver:

1. **Descarte de Filas Vacías y Basura de Entrada:**  
   Filtro automático que descarta registros `NULL` o líneas de separación residuales del archivo original en la transición a Plata.

2. **Limpieza de Texto y Tipado Estricto (Existente):**  
   - TRIM, Mayúsculas, remoción de tildes/ñ y sanitización de puntos/comas de miles.
   - Tipado estricto nativo en DuckDB (`DOUBLE`, `DATE`, `ENUM`, `BIGINT`).
   - Imputación condicional de nulos por grupo (`AVG() OVER (PARTITION BY categoria, moneda)`).

3. **Segmentación Dimensional (3 Datasets Parquet):**  
   Reestructuración para dividir el dataset monolítico en 3 entidades relacionales con `PK` y `FK`:
   - `dim_usuarios.parquet`
   - `dim_cuentas.parquet`
   - `fact_asientos_contables.parquet`

4. **Constructor No-Code de Columnas Calculadas:**  
   Interfaz intuitiva para crear campos numéricos/financieros (ej: `MONTO_LOCAL = ENTERED_DR * TASA_CAMBIO`).

5. **VLOOKUP Visual (Enriquecimiento por Llave):**  
   Cruce de tablas sin necesidad de escribir SQL manual.

---

## 🥇 5. Capa GOLD (Oro / Consumo, Modelos Matemáticos y LLM)

### 📌 Estado de la Capa Gold:
Capa de consumo de alto nivel para negocio, estados financieros y auditoría de riesgos.

1. **Datamarts Analíticos Pre-agrupados:**  
   Balances por Libro (`gold_balance_by_ledger.parquet`) y Estado de Resultados PyG por Cuentas (`gold_balance_by_account.parquet`).

2. **Catálogo de Modelos Matemáticos Financieros Pre-definidos:**  
   Plantillas No-Code donde el usuario asigna 3 o 4 variables de entrada (Margen Operacional, Razón Corriente, Z-Score de atípicos).

3. **Auditoría Semántica y NLP con LLM Pequeño:**  
   Evaluación inteligente de notas/descripciones contables y alertas de segregación de funciones (`creado_por == aprobado_por`).

---

## 📑 6. Conclusión
- **Bronze:** Ya cuenta con la autodetección nativa de delimitador y encodings en DuckDB (`read_csv_auto`). No requiere trabajo adicional de UI.
- **Silver:** Centraremos la reestructuración en la **segmentación de los 3 Datasets Parquet** (`dim_usuarios`, `dim_cuentas`, `fact_asientos`) y la herramienta de **Columnas Calculadas No-Code**.
- **Gold:** Recibirá la capa semántica con los **Modelos Matemáticos** y la **Auditoría NLP con LLM**.
