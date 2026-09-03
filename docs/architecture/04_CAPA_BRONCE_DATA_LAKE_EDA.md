# 🥉 04. CAPA BRONCE: DATA LAKE & DIAGNÓSTICO EDA CRUDO
### Ingesta Atómica, Custodia Criptográfica & Diagnóstico Físico de Calidad
**Proyecto de Maestría en Analítica de Datos | Stack: DuckDB Native, Parquet, SHA-256**

---

## 📌 1. RESPONSABILIDAD DE LA CAPA BRONCE

La Capa Bronce representa el **Data Lake Crudo Inmutable**. Su responsabilidad es ingerir extractos contables de Oracle EBS, SAP S/4HANA, MS Dynamics o CSVs externos y almacenarlos en su formato físico original sin modificar la información de negocio.

---

## 📐 2. COMPONENTES Y MECANISMOS FÍSICOS

### 1. Ingesta Atómica Parquet con Escritura Segura (`atomic_parquet_writer.py`)
Para evitar corrupción de datos por fallos de red, cortes de energía o terminación de procesos durante la conversión de CSV a Parquet, la infraestructura utiliza un patrón de **Escritura Atómica en dos pasos**:
1. DuckDB escribe el dataset resultado en un archivo Parquet temporal `.tmp`.
2. Una vez finalizada la copia física y verificado el total de registros, se ejecuta una operación atómica a nivel del sistema operativo (`Path.replace()`) sustituyendo el archivo objetivo.

```python
# Módulo de Infraestructura: atomic_parquet_writer.py
def execute_atomic_parquet_copy(conn, select_sql: str, target_path: Path) -> None:
    temp_path = target_path.parent / f".tmp_{target_path.name}"
    safe_temp = str(temp_path.resolve()).replace("'", "''")
    
    copy_sql = f"COPY ({select_sql}) TO '{safe_temp}' (FORMAT PARQUET, COMPRESSION SNAPPY)"
    conn.execute(copy_sql)
    
    # Reemplazo atómico a nivel OS
    temp_path.replace(target_path)
```

---

### 2. Cadena de Custodia Criptográfica (Firma SHA-256)
Para responder a requerimientos de auditoría forense legal e inmutabilidad de la evidencia:
- Al momento de ingestar el dataset crudo, el sistema calcula el hash **SHA-256 del contenido del archivo**.
- La firma digital resultante se registra en la receta y en la memoria del proyecto.
- Cualquier modificación manual o alteración maliciosa en los bytes del archivo `bronze.parquet` provocará una invalidez inmediata del hash, alertando al auditor sobre una violación de la cadena de custodia.

---

### 3. Diagnóstico Físico Exploratorio (EDA Crudo) Vectorizado
La Capa Bronce ejecuta un profilado estadístico físico sobre `bronze.parquet` utilizando una **única consulta vectorizada de DuckDB** para evitar múltiples escaneos de disco:

```sql
-- Consulta SQL Vectorizada de Profilado Físico Bronce
SELECT 
    COUNT(*) AS total_rows,
    COUNT(column_name) AS non_null_count,
    COUNT(DISTINCT column_name) AS unique_count,
    MEAN(CAST(column_name AS DOUBLE)) AS mean_value,
    MIN(CAST(column_name AS DOUBLE)) AS min_value,
    MAX(CAST(column_name AS DOUBLE)) AS max_value,
    SUM(CAST(column_name AS DOUBLE)) AS sum_value
FROM read_parquet('data/projects/makro/bronze/bronze.parquet');
```

#### Métricas Calculadas en Bronce:
- **Total de Filas y Columnas:** Conteo físico de registros.
- **Salud de Nulos (%):** Porcentaje de vacíos y detección de cadenas de texto vacías `""`.
- **Columnas Constantes (0 Varianza):** Columnas con 1 solo valor único que no aportan información.
- **Estadísticas Descriptivas Crudas:** Media ($\mu$), Mínimo, Máximo y Suma Total Cruda sobre columnas de importes y montos.
