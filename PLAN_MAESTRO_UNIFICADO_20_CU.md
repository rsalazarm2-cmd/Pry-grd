# 🏛️ PLAN MAESTRO UNIFICADO: 20 CASOS DE USO DE AUDITORÍA FORENSE
### Sistema de Auditoría Forense Financiera & Arquitectura Medallion (Bronce, Plata, Oro)
**Maestría en Analítica de Datos | Stack: DuckDB Nativo, Python/Django Ninja, Vue 3/TypeScript, Parquet**

> **Este documento es la ÚNICA fuente de verdad del proyecto.** Sustituye y consolida los documentos anteriores:
> `PLAN_MAESTRO_15_CASOS_DE_USO.md`, `PLAN_MAESTRO_INGENIERIA_DATOS.md` y `PLAN_MAESTRO_SUPERPODERES_AUDITORIA.md`.

---

## 📌 PRINCIPIOS DE DISEÑO INQUEBRANTABLES

1. **Regla de las 200 Líneas:** Ningún archivo `.py` o `.ts` supera las 200 líneas. Módulos atómicos.
2. **Clean Architecture / Hexagonal:** `api/` (Router) → `application/` (Casos de Uso) → `infrastructure/` (DuckDB/FS) → `domain/` (DTOs Pydantic).
3. **Tipado Estricto:** Type Hints en Python, Strict Mode en TypeScript. Cero `Any` genéricos.
4. **Responsabilidad Única (SRP):** Cada función hace UNA sola cosa. Early Returns. Cero anidamientos profundos.
5. **Gestor de Paquetes:** `uv` para Python.
6. **División Medallion:**
   - **Bronce:** Data Lake Crudo, Ingesta Atómica, SHA-256, Diagnóstico Físico EDA.
   - **Plata:** Estandarización (33 Campos Canónicos), Deltas de Fechas, Split Cargo/Abono, Linaje, Memoria JSON.
   - **Oro:** Matrices de Correlación, Detección Z-Score, Benford, Shannon, Mahalanobis, Auditoría SOX.

---

## 🎯 DEFINICIÓN DE "CASO DE USO REAL" EN ESTE PROYECTO

> Un Caso de Uso Real **NO** es "hacer clic en un botón". Es una **secuencia de transformación matemática, filtrado, agregación y/o visualización interactiva** donde el auditor opera sobre datos contables para descubrir patrones, atípicos y riesgos.

---

## 📋 MATRIZ COMPLETA DE LOS 20 CASOS DE USO

---

### 🔹 FASE 1: Motor AST de Expresiones Vectorizadas & Separador de Partida Doble
**Capa:** Plata | **Complejidad:** Alta | **Foco:** Cómputo vectorizado DuckDB para fechas y montos

#### CU-01: Inspección Visual de Redundancia de Fechas (% Match) y Decisión de Descarte

- **Manejo de Data:** Cálculo en DuckDB del porcentaje de coincidencia exacta entre $N$ columnas de fecha:
  $$\text{\% Coincidencia} = \frac{\text{Count}(\text{FECHA\_A} == \text{FECHA\_B})}{\text{Total Filas}} \times 100\%$$
- **Visualización:** Si el indicador muestra `100% Idénticas`, el auditor descarta las fechas redundantes conservando solo 1 columna.
- **Entregable Backend:** `silver_date_expression_engine.py` — función `compute_date_redundancy_matrix()`.
- **Entregable Frontend:** Componente visual con indicador neón de redundancia %.

#### CU-02: Pareo Dinámico de Fechas y Generación de Columna Delta (`DIFERENCIA_SEGUNDOS`)

- **Manejo de Data:** Si la coincidencia es $<100\%$, el auditor selecciona `FECHA_REGISTRO` y `FECHA_POSTEO` para generar:
  $$T_{\text{delta\_seconds}} = \text{DATEDIFF}('second', \text{FECHA\_REGISTRO}, \text{FECHA\_CONTABILIZACION})$$
- **Visualización:** Histograma interactivo de distribuciones de tiempo de aprobación para aislar posteos de $<60$ segundos.
- **Entregable Backend:** `silver_date_expression_engine.py` — función `compile_date_delta()`.
- **Entregable Frontend:** Selector de pares de fechas + histograma con Plotly.

#### CU-03: Derivación de Día de la Semana e Identificación de Días No Hábiles

- **Manejo de Data:** Aplicación de:
  $$\text{DIA\_SEMANA} = \text{STRFTIME}(\text{FECHA\_CONTABILIZACION}, '\%A')$$
  $$\text{ES\_FIN\_DE\_SEMANA} = \text{CASE WHEN EXTRACT}(\text{DOW FROM FECHA}) \text{ IN } (0, 6) \text{ THEN TRUE END}$$
- **Visualización:** Columna `DIA_SEMANA` con resalte cromático neón en sábados/domingos.
- **Entregable Backend:** `silver_date_expression_engine.py` — función `derive_weekday_flags()`.

#### CU-04: Transformación/Split de 1 Columna Signada (+/-) a 2 Columnas (`CARGO` / `ABONO`)

- **Manejo de Data:** Transformación vectorizada:
  $$\text{CARGO} = \text{IF AMOUNT} > 0 \text{ THEN AMOUNT ELSE } 0.00$$
  $$\text{ABONO} = \text{IF AMOUNT} < 0 \text{ THEN } |\text{AMOUNT}| \text{ ELSE } 0.00$$
- **Visualización:** Previsualización en vivo de la separación de partidas deudoras/acreedoras.
- **Entregable Backend:** `silver_amount_splitter_engine.py` — función `split_signed_amount()`.

**Entregables Técnicos de Fase 1:**
| Archivo | Ubicación | Límite Líneas |
| :--- | :--- | :---: |
| `date_expression_ast.py` | `backend/src/silver/domain/` | < 100 |
| `silver_date_expression_engine.py` | `backend/src/silver/infrastructure/` | < 180 |
| `silver_amount_splitter_engine.py` | `backend/src/silver/infrastructure/` | < 100 |
| Composable `useSilverDateExpressions.ts` | `frontend/src/composables/` | < 120 |

---

### 🔹 FASE 2: Constructor Dinámico de Esquema & Canvas Visual (Capa Plata)
**Capa:** Plata | **Complejidad:** Alta | **Foco:** Pipeline Visual interactivo para el auditor

#### CU-05: Fragmentación/Filtrado de la Base de Datos en 2 Datasets (Cargos vs Abonos)

- **Manejo de Data:** Partición atómica de la base de datos para analizar separadamente movimientos deudores y acreedores.
- **Visualización:** Selector de vista que conmuta la tabla entre **Dataset de Cargos** y **Dataset de Abonos**.

#### CU-06: Selección, Reordenamiento y Reducción Visual de Campos (Schema Blueprint)

- **Manejo de Data:** Arrastre y supresión de columnas para reducir de $N$ columnas crudas a $M$ columnas estandarizadas.
- **Visualización:** Renderizado del plano del esquema (*Schema Blueprint*) antes de compilar a Parquet.
- **Entregable Frontend:** `SilverSchemaCanvas.vue` (< 180 líneas) — Canvas visual interactivo.

#### CU-07: Visualización de Linaje Transparente de Mapeo (`Columna Origen` → `Columna Plata`)

- **Manejo de Data:** Inspección del mapa de transformación: `Columna Origen` → `Nombre Plata`, tipo inferido, regla de imputación y calidad.
- **Visualización:** Matriz interactiva de trazabilidad con badges de integridad.
- **Entregable Frontend:** `SilverLineageTable.vue` (< 170 líneas).

#### CU-08: Persistencia Inmutable de Receta Contable (`.column_mapping_rules.json`)

- **Manejo de Data:** Guardado inmutable de reglas de mapeo por proyecto para reaplicación automática en **1 ms** en descargas mensuales futuras.
- **Visualización:** Badge de estado de la receta (activa/cargada/nueva).
- **Backend existente:** [mapping_rules_persistence_service.py](file:///home/rsalazar/Python/Pry_Grd/backend/src/bronze/infrastructure/mapping_rules_persistence_service.py) ✅

**Entregables Técnicos de Fase 2:**
| Archivo | Ubicación | Límite Líneas |
| :--- | :--- | :---: |
| `SilverSchemaCanvas.vue` | `frontend/src/components/forms/` | < 180 |
| `useSilverSchemaBuilder.ts` | `frontend/src/composables/` | < 150 |
| `schema_canvas.ts` | `frontend/src/types/` | < 90 |
| `SilverLineageTable.vue` | `frontend/src/components/analytics/` | < 170 |

---

### 🔹 FASE 3: Reglas Condicionales No-Code & Schema Preview
**Capa:** Plata | **Complejidad:** Alta | **Foco:** Evaluador dinámico de reglas del auditor sin código

#### CU-09: Reglas de Transformación Condicional `IF-THEN-ELSE` No-Code

- **Manejo de Data:** Evaluador dinámico donde el auditor define reglas de negocio sin escribir SQL:
  ```
  IF MONTO > 100000 AND DIA_SEMANA IN ('SÁBADO','DOMINGO') THEN RIESGO = 'CRÍTICO'
  IF USUARIO_REGISTRADOR == USUARIO_APROBADOR THEN FLAG_SOD = TRUE
  ```
- **Visualización:** Constructor visual de reglas con previsualización del resultado en tabla.
- **Entregable Backend:** `silver_rule_evaluator_engine.py` (< 150 líneas).
- **Entregable Frontend:** `ConditionalRuleBuilder.vue` (< 180 líneas).

#### CU-10: Previsualización de Esqueleto de Tabla Final (Schema Blueprint Preview)

- **Manejo de Data:** Visualización de la estructura resultante (nombres, tipos, reglas) antes de la compilación física a Parquet.
- **Visualización:** Vista previa del esquema Plata con tipos de datos, nulabilidad y reglas aplicadas.

**Entregables Técnicos de Fase 3:**
| Archivo | Ubicación | Límite Líneas |
| :--- | :--- | :---: |
| `silver_rule_evaluator_engine.py` | `backend/src/silver/infrastructure/` | < 150 |
| `rule_expression_dto.py` | `backend/src/silver/domain/` | < 80 |
| `ConditionalRuleBuilder.vue` | `frontend/src/components/forms/` | < 180 |

---

### 🔹 FASE 4: Modelado Estadístico Avanzado de Maestría (Capa Oro)
**Capa:** Oro | **Complejidad:** Muy Alta | **Foco:** Modelos estadísticos probados para detección de fraude

#### CU-11: Matriz Visual de Correlación Lineal de Pearson ($r$)

- **Manejo de Data:** Cómputo vectorizado en DuckDB de la matriz de correlación de Pearson ($r \in [-1.0, 1.0]$) sobre CARGO, ABONO, TASA_CAMBIO y volumen de líneas:
  $$r_{X,Y} = \frac{\sum (X_i - \bar{X})(Y_i - \bar{Y})}{\sqrt{\sum (X_i - \bar{X})^2 \sum (Y_i - \bar{Y})^2}}$$
- **Visualización:** Mapa de calor interactivo de correlación lineal (Plotly heatmap).

#### CU-12: Matriz Visual de Correlación de Rangos de Spearman ($\rho$) para Importes Sesgados

- **Manejo de Data:** Cómputo no paramétrico de Spearman para evaluar dependencias monótonas resistentes a outliers:
  $$\rho = 1 - \frac{6 \sum d_i^2}{n(n^2 - 1)}$$
- **Visualización:** Matriz comparativa Pearson vs Spearman lado a lado.

#### CU-13: Serie de Tiempo y Detección de Fechas Atípicas de Asientos Manuales ($Z$-Score)

- **Manejo de Data:** Agregación del volumen diario de asientos manuales (`ORIGEN_ASIENTO = 'MANUAL'`) y cálculo del Z-Score diario:
  $$Z_t = \frac{V_t - \mu_V}{\sigma_V}$$
- **Visualización:** Gráfico temporal resaltando picos anómalos con $Z_t \ge 2.5$.

#### CU-14: Comparativa de Distribución Paramétrica vs No-Paramétrica ($\mu$ vs $\tilde{x}$)

- **Manejo de Data:** Evaluación del sesgo (*Skewness*) comparando Media ($\mu$) vs Mediana ($\tilde{x}$) y StdDev ($\sigma$) vs IQR:
  $$\text{IQR} = Q_3 - Q_1$$
- **Visualización:** Diagrama de caja y bigotes (Tukey $1.5 \times \text{IQR}$) etiquetando importes atípicos.

#### CU-15: Test Forense de Ley de Benford (First-Digit & First-Two Digits)

- **Manejo de Data:** Evaluación de la frecuencia del primer dígito y comparación con la distribución teórica:
  $$P(d) = \log_{10}\left(1 + \frac{1}{d}\right) \quad d \in \{1, 2, ..., 9\}$$
  Cálculo de la **Desviación Absoluta Media (MAD)** para cuantificar la conformidad:
  $$\text{MAD} = \frac{1}{K} \sum_{d=1}^{K} |P_{\text{observada}}(d) - P_{\text{Benford}}(d)|$$
- **Visualización:** Gráfico de barras Frecuencia Observada vs Esperada (Benford) con umbral MAD.
- **Valor Académico:** Estándar ACFE (Association of Certified Fraud Examiners) para detección de fabricación numérica.

#### CU-16: Entropía de Información de Shannon ($H(X)$) sobre Glosas

- **Manejo de Data:** Cálculo de la entropía de Shannon sobre el campo `GLOSA_ASIENTO` para aislar texto aleatorio o descripciones repetitivas vacías:
  $$H(X) = -\sum P(x) \log_2 P(x)$$
  - **$H(X) \approx 0$** = todas las glosas son idénticas (posible copiar-pegar).
  - **$H(X)$ muy alto** = texto aleatorio/basura.
- **Visualización:** Histograma de entropía por grupo de asientos con umbrales de riesgo.
- **Valor Académico:** Aplicación innovadora de Teoría de la Información a auditoría financiera.

#### CU-17: Distancia Multivariada de Mahalanobis ($D^2$) para Anomalías Combinadas

- **Manejo de Data:** Detección de anomalías en la combinación (CARGO, ABONO, TASA_CAMBIO, LINEAS_ASIENTO) que no se detectan aisladamente en 1 sola variable:
  $$D^2 = (\mathbf{x} - \boldsymbol{\mu})^T \mathbf{S}^{-1} (\mathbf{x} - \boldsymbol{\mu})$$
  donde $\mathbf{S}$ es la matriz de covarianza y $\boldsymbol{\mu}$ el vector de medias.
- **Visualización:** Scatter plot con escala de color por distancia $D^2$ y umbral $\chi^2$.
- **Valor Académico:** Supera a Z-Score univariado. Detecta combinaciones atípicas multivariadas.

**Entregables Técnicos de Fase 4:**
| Archivo | Ubicación | Límite Líneas |
| :--- | :--- | :---: |
| `gold_correlation_engine.py` | `backend/src/gold/infrastructure/` | < 180 |
| `gold_benford_engine.py` | `backend/src/gold/infrastructure/` | < 150 |
| `gold_shannon_engine.py` | `backend/src/gold/infrastructure/` | < 120 |
| `gold_mahalanobis_engine.py` | `backend/src/gold/infrastructure/` | < 150 |
| `gold_zscore_engine.py` | `backend/src/gold/infrastructure/` | < 120 |
| `gold_analytics_router.py` | `backend/src/gold/api/` | < 120 |
| `gold_analytics_dtos.py` | `backend/src/gold/domain/` | < 100 |
| `GoldWorkspace.vue` (refactored) | `frontend/src/views/` | < 180 |
| `CorrelationHeatmap.vue` | `frontend/src/components/charts/` | < 150 |
| `BenfordChart.vue` | `frontend/src/components/charts/` | < 150 |
| `ZScoreTimeline.vue` | `frontend/src/components/charts/` | < 150 |
| `useGoldAnalytics.ts` | `frontend/src/composables/` | < 130 |

---

### 🔹 FASE 5: Command Center Ejecutivo SOX & Evidencia Forense Inviolable
**Capa:** Oro + Auditoría | **Complejidad:** Muy Alta | **Foco:** KPIs monetarios ($) y exportación SHA-256

#### CU-18: Cuantificación Monetaria ($) de SoD + Grafo de Relaciones Maker-Checker

- **Manejo de Data:** Filtrado y suma monetaria de asientos donde $\text{USUARIO\_REGISTRADOR} == \text{USUARIO\_APROBADOR}$:
  $$\text{Riesgo SoD}(\$) = \sum \text{CARGO\_MONEDA\_FUNCIONAL} \text{ WHERE Maker} = \text{Checker}$$
  Mapeo de red entre `USUARIO_REGISTRADOR` y `USUARIO_APROBADOR` para descubrir patrones de colusión.
- **Visualización:** Tarjeta KPI de impacto financiero ($) + Grafo visual de red Maker-Checker (D3.js o vis-network).

#### CU-19: Detector de Fragmentación de Montos (Smurfing / Splitting)

- **Manejo de Data:** Identificación de múltiples asientos creados el mismo día por un mismo usuario con montos justo debajo del umbral de aprobación (ej. $9,999 para evadir $10,000):
  ```sql
  SELECT USUARIO_REGISTRADOR, FECHA_CONTABILIZACION, COUNT(*) AS n_asientos,
         SUM(CARGO_MONEDA_FUNCIONAL) AS total_fragmentado
  FROM silver
  WHERE CARGO_MONEDA_FUNCIONAL BETWEEN (UMBRAL * 0.90) AND UMBRAL
  GROUP BY USUARIO_REGISTRADOR, FECHA_CONTABILIZACION
  HAVING COUNT(*) >= 3
  ```
- **Visualización:** Tabla de alertas con usuario, fecha, cantidad de fragmentos y monto total acumulado.
- **Valor Académico:** Técnica AML (Anti-Money Laundering) aplicada a auditoría interna.

#### CU-20: Exportación de Expediente de Evidencia Forense con Sello SHA-256

- **Manejo de Data:** Consolidación de todas las evidencias de auditoría (descuadres, SoD, aprobaciones < 60s, montos redondos, Benford, smurfing) en un expediente inmutable con:
  - Resumen ejecutivo de hallazgos
  - Detalle de alertas por categoría de riesgo
  - Firma SHA-256 de cadena de custodia
- **Visualización:** Exportación PDF/CSV firmado digitalmente.
- Incluye cuantificación de aprobaciones exprés (< 60 segundos) y montos redondos elevados (> $100,000 terminados en `.00`).

**Entregables Técnicos de Fase 5:**
| Archivo | Ubicación | Límite Líneas |
| :--- | :--- | :---: |
| `forensic_sod_engine.py` | `backend/src/audit/infrastructure/` | < 170 |
| `forensic_smurfing_engine.py` | `backend/src/audit/infrastructure/` | < 130 |
| `forensic_export_service.py` | `backend/src/audit/infrastructure/` | < 150 |
| `audit_router.py` | `backend/src/audit/api/` | < 120 |
| `audit_risk_dtos.py` | `backend/src/audit/domain/` | < 100 |
| `AuditWorkspace.vue` (refactored) | `frontend/src/views/` | < 180 |
| `SodGraph.vue` | `frontend/src/components/audit/` | < 170 |
| `SmurfingAlertTable.vue` | `frontend/src/components/audit/` | < 150 |
| `useForensicAudit.ts` | `frontend/src/composables/` | < 130 |

---

## 🧪 ESTRATEGIA DE TESTING Y VERIFICACIÓN (TRANSVERSAL)

### Ubicación: `qa_environment/` (estructura existente)

#### Pytest (Backend)
| Test File | Qué Verifica | Fase |
| :--- | :--- | :---: |
| `test_date_expression_engine.py` | Deltas, redundancia %, día de semana | F1 |
| `test_amount_splitter.py` | Split de columna signada a Cargo/Abono | F1 |
| `test_schema_builder.py` | Reducción de N→M columnas | F2 |
| `test_mapping_persistence.py` | Guardado/carga de `.column_mapping_rules.json` | F2 |
| `test_rule_evaluator.py` | Reglas IF-THEN-ELSE condicionales | F3 |
| `test_pearson_spearman.py` | Matrices de correlación con datos sintéticos conocidos | F4 |
| `test_zscore_detection.py` | Detección de picos anómalos con Z ≥ 2.5 | F4 |
| `test_benford.py` | Validación de MAD contra distribución conocida de Benford | F4 |
| `test_shannon_entropy.py` | Entropía = 0 para datos idénticos, > 0 para variados | F4 |
| `test_mahalanobis.py` | Anomalías multivariadas con datos controlados | F4 |
| `test_sod_detection.py` | Detectar Maker == Checker correctamente | F5 |
| `test_smurfing_detection.py` | Detectar fragmentación justo debajo del umbral | F5 |
| `test_forensic_export.py` | Hash SHA-256 del expediente es determinista | F5 |

#### Vitest (Frontend)
| Test File | Qué Verifica | Fase |
| :--- | :--- | :---: |
| `useSilverDateExpressions.test.ts` | Composable retorna estado correcto | F1 |
| `useGoldAnalytics.test.ts` | Composable maneja loading/error/data | F4 |
| `useForensicAudit.test.ts` | Composable de auditoría | F5 |

#### Validación Cruzada Independiente
- **Jupyter Notebook** (`qa_environment/notebooks/validacion_cruzada.ipynb`): Calcula Pearson, Spearman, Z-Score, Benford MAD y Shannon con `scipy` y `pandas` como control independiente del backend DuckDB.

---

## 📅 CRONOGRAMA DE EJECUCIÓN MATRIZ

| Fase | Descripción | CU Asignados | Entregable Principal | Complejidad | Estado |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **F1** | Motor AST + Split Cargo/Abono | CU-01, CU-02, CU-03, CU-04 | `silver_date_expression_engine.py` | **Alta** | ⏳ |
| **F2** | Canvas Visual + Linaje + Persistencia | CU-05, CU-06, CU-07, CU-08 | `SilverSchemaCanvas.vue` | **Alta** | ⏳ |
| **F3** | Reglas No-Code + Schema Preview | CU-09, CU-10 | `silver_rule_evaluator_engine.py` | **Alta** | ⏳ |
| **F4** | Pearson, Spearman, Z-Score, Benford, Shannon, Mahalanobis | CU-11 a CU-17 | `gold_*_engine.py` (5 motores) | **Muy Alta** | ⏳ |
| **F5** | Command Center SOX + Smurfing + SHA-256 | CU-18, CU-19, CU-20 | `AuditWorkspace.vue` refactored | **Muy Alta** | ⏳ |

---

## 📊 MATRIZ DE SUPERPODERES DEL AUDITOR POR FASE

| Fase | Superpoderes | Valor Académico |
| :--- | :--- | :--- |
| **F1** | Deltas de fecha en microsegundos, Split de partida doble, Detección de fin de semana | Cómputo vectorizado OLAP |
| **F2** | Schema Canvas drag-and-drop, Linaje Bronce→Plata, Memoria JSON de 1 ms | Data Pipeline Visual |
| **F3** | Reglas IF-THEN-ELSE No-Code, Blueprint interactivo | Evaluador dinámico de auditoría |
| **F4** | Pearson $r$, Spearman $\rho$, Z-Score temporal, **Benford MAD**, **Shannon $H(X)$**, **Mahalanobis $D^2$** | Estadística Avanzada + Teoría de la Información |
| **F5** | Grafo SoD Maker-Checker, **Smurfing/Splitting**, Expediente SHA-256 | Auditoría Forense SOX 404 |

---

## 🗺️ DEPENDENCIAS ENTRE FASES

```
Fase 1 (AST + Split)
  ├──→ Fase 2 (Canvas + Linaje) ──→ Fase 3 (Reglas No-Code)
  │                                        │
  └────────────────────→ Fase 4 (Estadística Oro) ←──────────┘
                                   │
                                   └──→ Fase 5 (Command Center SOX)
```

> **Camino crítico:** F1 → F4 → F5 (la estadística avanzada depende de que la Capa Plata esté limpia, y el Command Center depende de los modelos Oro).

---

## 📐 JUSTIFICACIÓN ARQUITECTÓNICA PARA LA TESIS

1. **Modularidad verificable:** La regla de 200 líneas + SRP garantiza que cada módulo se puede testear aisladamente con pytest.
2. **Separación de capas Medallion:** Permite al comité evaluador trazar el flujo de datos desde el CSV crudo hasta el dictamen forense.
3. **Fundamentación matemática:** 7 modelos estadísticos formales (Pearson, Spearman, Z-Score, Benford, Shannon, Mahalanobis, Tukey IQR) con fórmulas explícitas.
4. **Aplicabilidad profesional real:** SoD, Smurfing y SHA-256 son estándares de auditoría SOX 404 y AML usados en Big 4 (Deloitte, PwC, EY, KPMG).
5. **Rendimiento en PC de escritorio:** DuckDB + Parquet + procesamiento vectorizado SIMD permite procesar >100,000 registros en <50 ms sin servidor.
