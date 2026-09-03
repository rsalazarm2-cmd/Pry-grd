# 🖥️ 02. DESEMPEÑO EN PC DE ESCRITORIO Y OPTIMIZACIÓN
### Análisis de Rendimiento Físico en Servidores / PCs Locales
**Proyecto de Maestría en Analítica de Datos | Stack: DuckDB, Parquet, SIMD, SHA-256**

---

## 📌 1. ¿POR QUÉ ES LA ARQUITECTURA ÓPTIMA PARA ESCRITORIO?

Procesar millones de asientos contables en un PC de escritorio local solía presentar cuellos de botella por el uso de motores relacionales cliente-servidor (Postgres/MySQL) o librerías en Python (Pandas/Spark) que consumen demasiada RAM.

Nuestra arquitectura resuelve este desafío mediante cuatro pilares físicos:

---

## ⚡ 2. PILARES FÍSICOS DE RENDIMIENTO

### 1. DuckDB: Motor OLAP Columnar In-Process (C++)
- **Cero Latencia de Socket TCP:** DuckDB corre dentro de la misma memoria del proceso Python.
- **Procesamiento Vectorizado por Bloques:** Procesa datos en bloques de 2048 tuplas aprovechando las instrucciones **SIMD (Single Instruction Multiple Data)** de CPUs Intel/AMD modernas.
- **Multi-threading Automático:** Distribución automática del trabajo sobre el 100% de los núcleos de la CPU del escritorio.

### 2. Apache Parquet: Formato Columnar Compreso
- **Compresión 10x-50x:** Los Parquets comprimen con Snappy/ZSTD reduciendo drásticamente la lectura de disco.
- **Projection Pushdown:** DuckDB solo lee del disco las columnas requeridas por la consulta SQL, reduciendo I/O a milisegundos.

### 3. Memoria Caché SHA-256 (1 ms)
- Las operaciones costosas (profiling e inferencia de IA) se persisten en caché indexada por la firma SHA-256 del dataset. Consultas secundarias responden en **1 milisegundo**.
