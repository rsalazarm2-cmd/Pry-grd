# 🥈 05. CAPA PLATA: ESTANDARIZACIÓN, AST DE FECHAS & LINEAJE
### Schema Canvas Interactivo, Deltas Temporales, Benford, Entropía & Memoria Inmutable
**Proyecto de Maestría en Analítica de Datos | Stack: DuckDB AST, Pydantic DTOs, JSON Schema**

---

## 📌 1. RESPONSABILIDAD Y CAPACIDADES DE LA CAPA PLATA

La Capa Plata es el corazón de **Transformación, Estandarización y Trazabilidad** del sistema. Recibe los Parquets crudos de Bronce y genera el archivo purificado `silver.parquet` alineado a la taxonomía canónica de 33 campos.

---

## 📐 2. ESPECIFICACIÓN DETALLADA DE SUPERPODERES Y TRANSFOMACIONES

### 1. Motor AST Vectorizado de Fechas
- **Cómputo de Deltas Temporales ($T_{\text{delta}}$):** Resta exacta vectorizada en DuckDB entre dos fechas:
  ```sql
  DATEDIFF('second', FECHA_REGISTRO_CONTABLE, FECHA_CONTABILIZACION) AS DIFERENCIA_SEGUNDOS_APROBACION
  ```
- **Extracción del Día de la Semana:**
  ```sql
  STRFTIME(FECHA_CONTABILIZACION, '%A') AS DIA_SEMANA_CONTABLE
  ```
- **Flag de Fin de Semana:**
  ```sql
  CASE WHEN EXTRACT(DAYOFWEEK FROM FECHA_CONTABILIZACION) IN (0, 6) THEN TRUE ELSE FALSE END AS ES_FIN_DE_SEMANA
  ```
- **Diagnosticador de Redundancia Temporal (% Match):**
  Matriz de coincidencia exacta entre pares de fechas para informar al auditor si 1 sola fecha es suficiente:
  $$\text{\% Coincidencia} = \frac{\text{Count}(\text{FECHA\_A} == \text{FECHA\_B})}{\text{Total Filas}} \times 100\%$$

### 2. Amount Splitter Engine (Cargos / Abonos)
Transforma 1 columna de monto signado (+/-) en 2 columnas independientes o separa el dataset:
```sql
CASE WHEN AMOUNT > 0 THEN AMOUNT ELSE 0.00 END AS CARGO_MONEDA_FUNCIONAL,
CASE WHEN AMOUNT < 0 THEN ABS(AMOUNT) ELSE 0.00 END AS ABONO_MONEDA_FUNCIONAL
```

### 3. Prueba Forense de Ley de Benford (MAD)
Cómputo de la frecuencia observada del primer dígito $P(d)$ vs la distribución teórica $P(d) = \log_{10}(1 + \frac{1}{d})$ y su **Desviación Absoluta Media (MAD)**:
$$\text{MAD} = \frac{1}{9} \sum_{d=1}^9 | P_{\text{observado}}(d) - P_{\text{Benford}}(d) |$$

### 4. Entropía de Información de Shannon ($H(X)$)
Medición de la aleatoriedad o patrones repetitivos vacíos en las glosas contables:
$$H(X) = -\sum_{i=1}^n P(x_i) \log_2 P(x_i)$$

### 5. Trazabilidad de Linaje & Memoria (`.column_mapping_rules.json`)
Tabla de linaje `Origen (Bronce)` ➔ `Plata` y memoria local inmutable guardada en `data/projects/{project_id}/.column_mapping_rules.json` para ejecutar mapeos recurrentes en **1 ms**.
