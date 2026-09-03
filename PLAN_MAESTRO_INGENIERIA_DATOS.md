# 🏛️ PLAN MAESTRO DE INGENIERÍA DE DATOS Y ANALÍTICA AVANZADA (5 FASES)
### Sistema de Auditoría Forense Financiera & Arquitectura Medallion (Bronce, Plata, Oro)
**Proyecto de Maestría en Analítica de Datos | Stack: DuckDB Nativo, Python/Django, Vue3/TypeScript, Parquet**

---

## 📌 RESUMEN DE ARQUITECTURA Y PRINCIPIOS DE DISEÑO

1. **Restricción de Oro (Inquebrantable):** Ningún archivo de código (Python o TypeScript) superará las **200 líneas**. Módulos atómicos, alta cohesión y bajo acoplamiento.
2. **Clean Architecture / Hexagonal:** Controllers (Ninja API) ➔ Services (Casos de Uso) ➔ Repositories (DuckDB / Filesystem) ➔ Domain (DTOs Pydantic).
3. **División Estricta Medallion:**
   - **Bronce:** Data Lake Crudo, Ingesta Atómica, Diagnóstico Físico EDA.
   - **Plata:** Estandarización de Esquema, Reducción de Campos, Deltas de Fechas, Días de la Semana, Trazabilidad y Memoria de Mapeo.
   - **Oro:** Data Marts, Matrices Pearson/Spearman, Detección Z-Score de Fechas Atípicas y KPIs de Impacto Financiero ($).

---

## 🚀 FASE 1: Motor de Expresiones Vectorizadas y AST de Fechas (Backend DuckDB)
**Objetivo:** Construir la infraestructura DuckDB nativa en Python encargada de evaluar y compilar expresiones vectorizadas de fecha a nivel de microsegundos.

### 📐 Fundamento Matemático & Expresiones SQL
- **Diferencia entre Pares de Fechas (Deltas Temporales):**
  $$T_{\text{delta\_seconds}} = \text{DATEDIFF}('second', \text{FECHA\_REGISTRO}, \text{FECHA\_CONTABILIZACION})$$
  $$T_{\text{delta\_days}} = \text{DATEDIFF}('day', \text{FECHA\_REGISTRO}, \text{FECHA\_CONTABILIZACION})$$
- **Extracción de Nombre de Día & Flag de Fin de Semana:**
  $$\text{DIA\_SEMANA} = \text{STRFTIME}(\text{FECHA\_CONTABILIZACION}, '\%A')$$
  $$\text{ES\_FIN\_DE\_SEMANA} = \text{CASE WHEN EXTRACT}(\text{DAYOFWEEK FROM FECHA}) \text{ IN } (0, 6) \text{ THEN TRUE ELSE FALSE END}$$

### 🛠️ Entregables Técnicos
1. `backend/src/silver/domain/date_expression_ast.py` (< 100 líneas): DTOs Pydantic `DateExpressionDTO`, `CalculatedFieldDTO`.
2. `backend/src/silver/infrastructure/silver_date_expression_engine.py` (< 180 líneas): Compilador SQL DuckDB nativo.
3. Pruebas de rendimiento vectorizado sobre parquets de > 100,000 registros (< 50 ms).

---

## 🎨 FASE 2: Constructor Dinámico de Esquema y Canvas Visual de Capa Plata (Frontend Canvas)
**Objetivo:** Desarrollar el constructor interactivo visual (*Data Pipeline Builder*) donde el auditor organiza, selecciona, reordena y calcula campos antes de ejecutar la Capa Plata.

### 📐 Funcionalidades Visuales
1. **Selector Interactivo de Deltas de Fechas:** Interfaz para elegir `Fecha A` vs `Fecha B` y generar el cálculo `DIFERENCIA_SEGUNDOS`.
2. **Extractor Visual de Día de la Semana:** Switch de un clic para derivar `DIA_SEMANA_CONTABLE`.
3. **Reordenamiento & Reducción de Columnas:** Control drag-and-drop / checkboxes para reducir de $N$ columnas crudas a $M$ columnas estandarizadas.
4. **Previsualización de Esqueleto de Tabla (Schema Blueprint):** Visualizador del esquema resultante antes de la compilación física.

### 🛠️ Entregables Técnicos
1. `frontend/src/components/forms/SilverSchemaCanvas.vue` (< 180 líneas): Canvas visual interactivo.
2. `frontend/src/composables/useSilverSchemaBuilder.ts` (< 150 líneas): Composable de gestión de estado del pipeline.
3. `frontend/src/types/schema_canvas.ts` (< 90 líneas): Tipado TypeScript estricto.

---

## 🧬 FASE 3: Motor de Trazabilidad, Linaje Inmutable y Persistencia (.column_mapping_rules.json)
**Objetivo:** Garantizar la transparencia total de la transformación (*Data Lineage*) y la memoria contable del proyecto para cargas incrementales recurrentes.

### 📐 Mapeo de Linaje Contable
- **Tabla de Trazabilidad Transparente:**
  $$\text{Columna Origen (Bronce)} \longrightarrow \text{Regla de Transformación} \longrightarrow \text{Columna Estandarizada (Plata)}$$
- **Persistencia en 1 ms:** Guardar la receta contable en `data/projects/{project_id}/.column_mapping_rules.json` para omitir el modelo NLP en ejecuciones futuras con la misma estructura.

### 🛠️ Entregables Técnicos
1. `frontend/src/components/analytics/SilverLineageTable.vue` (< 170 líneas): Tabla de linaje dinámico.
2. `backend/src/bronze/infrastructure/mapping_rules_persistence_service.py` (< 120 líneas): Gestor inmutable JSON.
3. Integración completa en `SilverWorkspace.vue`.

---

## 📊 FASE 4: Modelado Estadístico Avanzado de Maestría (Pearson, Spearman y Z-Score en Capa Oro)
**Objetivo:** Elevar el análisis contable a grado científico mediante modelos estadísticos probados para la detección de fraude e irregularidades.

### 📐 Modelos Matemáticos Probados
1. **Matriz de Correlación de Pearson ($r$):**
   $$r_{X,Y} = \frac{\sum (X_i - \bar{X})(Y_i - \bar{Y})}{\sqrt{\sum (X_i - \bar{X})^2 \sum (Y_i - \bar{Y})^2}}$$
2. **Matriz de Correlación de Spearman ($\rho$):**
   $$\rho = 1 - \frac{6 \sum d_i^2}{n(n^2 - 1)}$$
3. **Detección Temporal de Fechas Atípicas en Asientos Manuales ($Z$-Score):**
   $$Z_t = \frac{V_t - \mu_V}{\sigma_V} \quad \text{donde } V_t \text{ es el volumen diario de } \text{ORIGEN\_ASIENTO} = \text{'MANUAL'}$$
   *Una fecha se clasifica como atípica si $Z_t \ge 2.5$ o si ocurre en fin de semana.*
4. **Comparativa Paramétrica vs No-Paramétrica:**
   Media ($\mu$) vs Mediana ($\tilde{x}$), Desviación Estándar ($\sigma$) vs Rango Intercuartílico ($\text{IQR} = Q_3 - Q_1$), Asimetría (*Skewness*).

### 🛠️ Entregables Técnicos
1. `backend/src/gold/infrastructure/gold_analytics_engine.py` (< 190 líneas): Consultas SQL DuckDB vectorizadas para Pearson, Spearman y Z-Score.
2. `backend/src/gold/api/gold_analytics_router.py` (< 120 líneas): API REST Ninja para los modelos estadísticos.
3. `frontend/src/views/GoldWorkspace.vue` (< 180 líneas): Workspace con matrices de correlación y mapa de calor de fechas atípicas.

---

## 🛡️ FASE 5: Command Center Ejecutivo de Auditoría SOX & Control Interno (KPIs Monetarios)
**Objetivo:** Unificar la evidencia contable en un tablero ejecutivo enfocado en el impacto monetario real ($) y la segregación de funciones.

### 📐 KPIs de Riesgo Financiero ($)
1. **Riesgo SoD ($):** Monto total de asientos donde $\text{USUARIO\_REGISTRADOR} == \text{USUARIO\_APROBADOR}$.
2. **Riesgo Posteo Neón ($):** Monto total posteado en $< 60$ segundos.
3. **Riesgo Fin de Semana ($):** Monto total contabilizado en sábados y domingos.
4. **Partida Doble Descuadrada ($):** Suma absoluta de desbalances por comprobante.

### 🛠️ Entregables Técnicos
1. `frontend/src/views/AuditWorkspace.vue` (< 180 líneas): Command Center Ejecutivo con gráficos interactivos.
2. `backend/src/audit/infrastructure/forensic_audit_service.py` (< 170 líneas): Motor de diagnóstico SOX.
3. Exportador de Informes Auditables en PDF/CSV con firma SHA-256 de cadena de custodia.

---

## 📅 CRONOGRAMA DE EJECUCIÓN MATRIZ

| Fase | Descripción | Entregable Principal | Estado |
| :--- | :--- | :--- | :---: |
| **Fase 1** | AST & Expresiones de Fechas | `silver_date_expression_engine.py` | ⏳ Pendiente |
| **Fase 2** | Canvas Visual de Esquema Plata | `SilverSchemaCanvas.vue` | ⏳ Pendiente |
| **Fase 3** | Linaje y Persistencia | `SilverLineageTable.vue` | ⏳ Pendiente |
| **Fase 4** | Pearson, Spearman & Z-Score | `GoldWorkspace.vue` | ⏳ Pendiente |
| **Fase 5** | Command Center SOX ($) | `AuditWorkspace.vue` | ⏳ Pendiente |
