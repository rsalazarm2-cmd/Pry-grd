# 📌 PLAN DE IMPLEMENTACIÓN - FASE 1
## Motor AST Vectorizado, Ley de Benford, Entropía de Shannon, Fechas y Amount Splitter (Backend DuckDB)
**Proyecto de Maestría en Analítica de Datos | Stack: Python, DuckDB Nativo, Pydantic V2**

---

## 🎯 OBJETIVO DE LA FASE 1
Construir el motor backend de infraestructura y dominio encargado de evaluar expresiones vectorizadas en DuckDB nativo para:
1. **Prueba de Ley de Benford (First & First-Two Digits Test):** Cómputo estadístico de la distribución del primer dígito $P(d) = \log_{10}(1 + \frac{1}{d})$ y cálculo de la **Desviación Absoluta Media (MAD)** sobre los montos para detectar manipulación o invención de cifras.
2. **Entropía de Información de Shannon ($H(X)$):** Cómputo de $H(X) = -\sum P(x) \log_2 P(x)$ sobre glosas y descripciones para aislar texto aleatorio o descripciones vacías repetitivas.
3. **Diferencias entre Pares de Fechas (Deltas Temporales):** Resta exacta en segundos/días entre columnas de fecha (`FECHA_REGISTRO` vs `FECHA_CONTABILIZACION`).
4. **Diagnosticador de Redundancia Temporal de Fechas (CU-01):** Matriz de coincidencia en % entre pares de fechas para informar si 1 sola fecha es suficiente.
5. **Separador Atómico de Cargos (Débitos) y Abonos (Créditos) (CU-04):** Transformador para separar 1 columna signada (+/-) en 2 columnas independientes `CARGO` y `ABONO`.

---

## 📐 CASOS DE USO REALES MAPEADOS

### 1. CU-01: Inspección Visual de Redundancia de Fechas (% Match)
- Cómputo en DuckDB del % de coincidencia exacta entre pares de fechas.

### 2. CU-02: Pareo Dinámico de Fechas y Generación de Columna Delta (`DIFERENCIA_SEGUNDOS`)
- Resta en segundos entre `FECHA_REGISTRO_CONTABLE` y `FECHA_CONTABILIZACION`.

### 3. CU-03: Derivación del Día de la Semana e Identificación de Días No Hábiles
- Evaluador de `STRFTIME(FECHA, '%A')` y flag booleano de fin de semana (`DAYOFWEEK IN (0, 6)`).

### 4. CU-04: Transformación/Split de 1 Columna Signada (+/-) a 2 Columnas (`CARGO` / `ABONO`)
- Transformación vectorizada de 1 columna signada a `CARGO` y `ABONO` independientes.

### 5. CU-20: Test Forense de Ley de Benford (MAD - Mean Absolute Deviation)
- **Fórmula:** $\text{MAD} = \frac{1}{9} \sum_{d=1}^9 | P_{\text{observado}}(d) - P_{\text{Benford}}(d) |$
- **Resultado:** Indicador numérico de invención deliberada de montos.

### 6. CU-21: Análisis de Entropía de Shannon ($H(X)$) en Descripciones y Glosas
- **Fórmula:** $H(X) = -\sum_{i=1}^n P(x_i) \log_2 P(x_i)$
- **Resultado:** Medida de aleatoriedad o patrones repetitivos vacíos en los textos contables.

---

## 🛠️ ESTRUCTURA Y ARCHIVOS A CREAR (< 200 LÍNEAS POR ARCHIVO)

### 1. `backend/src/silver/domain/date_expression_ast.py`
- DTOs Pydantic `DateDifferenceRuleDTO`, `BenfordAnalysisDTO`, `ShannonEntropyDTO`, `AmountSplitterRuleDTO`.

### 2. `backend/src/silver/infrastructure/silver_date_expression_engine.py`
- Compilador SQL DuckDB nativo con Benford, Shannon, deltas de fechas y split de montos.

### 3. `backend/src/silver/application/compile_silver_date_expressions_use_case.py`
- Caso de uso de compilación y análisis forense.

### 4. `backend/tests/test_silver_date_expression_engine.py`
- Test unitario Python evaluando Benford, Shannon, coincidencia % y split de montos en < 50 ms.

---

## 🧪 CRITERIOS DE ACEPTACIÓN Y VERIFICACIÓN
1. `uv run pytest tests/test_silver_date_expression_engine.py` en verde (0 fallos).
2. Ningún archivo supera las 200 líneas.
