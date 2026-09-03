# 🏛️ PLAN MAESTRO: 15 CASOS DE USO REALES DE MANEJO Y VISUALIZACIÓN DE DATOS
### Sistema de Auditoría Forense Financiera & Arquitectura Medallion (Bronce, Plata, Oro)
**Maestría en Analítica de Datos | Stack: DuckDB Nativo, Python/Django, Vue 3/TypeScript**

---

## 🎯 DEFINICIÓN DE UN CASO DE USO REAL EN INGENIERÍA Y ANALÍTICA DE DATOS
> **Regla del Proyecto:** Un "Caso de Uso" NO es *"hacer clic en un botón para abrir una pantalla"*. Un Caso de Uso Real es una **secuencia de transformación matemática, filtrado, agregación y visualización interactiva** donde el usuario opera sobre los datos contables para descubrir patrones, atípicos y riesgos de auditoría.

---

## 📋 MATRIZ DE LOS 15 CASOS DE USO DE MANEJO DE DATOS

### 🔹 SECCIÓN A: CANVAS DE MANEJO Y TRANSFORMACIÓN DE DATOS (CAPA PLATA)

#### 1. CU-01: Inspección Visual de Redundancia de Fechas (% Match) y Decisión de Descarte
- **Manejo de Data:** Cálculo en DuckDB del porcentaje de coincidencia exacta entre $N$ columnas de fecha:
  $$\text{\% Coincidencia} = \frac{\text{Count}(\text{FECHA\_A} == \text{FECHA\_B})}{\text{Total Filas}} \times 100\%$$
- **Visualización:** Si el indicador muestra **`100% Idénticas`**, el usuario descarta las fechas redundantes conservando solo 1 para limpiar la tabla Plata.

#### 2. CU-02: Pareo Dinámico de Fechas y Generación de Columna Delta (`DIFERENCIA_SEGUNDOS`)
- **Manejo de Data:** Si la coincidencia es $<100\%$, el usuario selecciona `FECHA_REGISTRO` y `FECHA_POSTEO` para generar la columna derivada `DIFERENCIA_SEGUNDOS_APROBACION`.
- **Visualización:** Histograma interactivo de distribuciones de tiempo de aprobación para aislar posteos de $<60$ segundos.

#### 3. CU-03: Derivación de Día de la Semana e Identificación de Días No Hábiles
- **Manejo de Data:** Aplicación de `STRFTIME(FECHA_CONTABILIZACION, '%A')` y evaluación de fin de semana (`DAYOFWEEK IN (0, 6)`).
- **Visualización:** Generación de `DIA_SEMANA` ('SÁBADO', 'DOMINGO') con resalte cromático neón en posteos fuera de calendario laboral.

#### 4. CU-04: Transformación/Split de 1 Columna Signada (+/-) a 2 Columnas (`CARGO` / `ABONO`)
- **Manejo de Data:** Transformación vectorizada de 1 columna de monto signado (+1,000 / -1,000) a 2 columnas independientes:
  $$\text{CARGO} = \text{IF } \text{AMOUNT} > 0 \text{ THEN } \text{AMOUNT} \text{ ELSE } 0.00$$
  $$\text{ABONO} = \text{IF } \text{AMOUNT} < 0 \text{ THEN } |\text{AMOUNT}| \text{ ELSE } 0.00$$
- **Visualización:** Previsualización en vivo de la separación de partidas dobles deudoras y acreedoras.

#### 5. CU-05: Fragmentación/Filtrado de la Base de Datos en 2 Datasets (Data de Cargos vs Data de Abonos)
- **Manejo de Data:** Partición o conmutación atómica de la base de datos para analizar separadamente movimientos deudores y acreedores.
- **Visualización:** Selector de vista que conmuta la tabla entre **Dataset de Cargos** y **Dataset de Abonos**.

#### 6. CU-06: Selección, Reordenamiento y Reducción Visual de Campos (Schema Blueprint)
- **Manejo de Data:** Arrastre y supresión de columnas para reducir de $N$ columnas crudas a $M$ columnas estandarizadas.
- **Visualización:** Renderizado del plano del esquema (*Schema Blueprint*) antes de compilar a Parquet.

#### 7. CU-07: Visualización de Linaje Transparente de Mapeo (`Columna Origen` ➔ `Columna Plata`)
- **Manejo de Data:** Inspección del mapa de metamorfosis: `Columna Origen` ➔ `Nombre Plata`, tipo inferido, regla de imputación (`0.00` para números, `'UNKNOWN'` para texto) y calidad.
- **Visualización:** Matriz interactiva de trazabilidad con badges de integridad.

#### 8. CU-08: Persistencia Inmutable de Receta Contable (`.column_mapping_rules.json`)
- **Manejo de Data:** Guardado inmutable de reglas de mapeo por proyecto para aplicar automáticamente en **1 ms** en descargas mensuales futuras.
- **Visualización:** Badge de memoria local activa con estado de la receta.

---

### 🔹 SECCIÓN B: ANALÍTICA ESTADÍSTICA Y MODELADO MATEMÁTICO (CAPA ORO)

#### 9. CU-09: Matriz Visual de Correlación Lineal de Pearson ($r$) entre Montos y Tasas
- **Manejo de Data:** Cómputo vectorizado en DuckDB de la matriz de correlación de Pearson ($r \in [-1.0, 1.0]$) sobre cargos, abonos, tasas de cambio y volumen de líneas.
- **Visualización:** Mapa de calor interactivo de correlación lineal.

#### 10. CU-10: Matriz Visual de Correlación de Rangos de Spearman ($\rho$) para Importes Sesgados
- **Manejo de Data:** Cómputo no paramétrico de Spearman para evaluar dependencias monótonas resistentes a outliers.
- **Visualización:** Matriz comparativa Pearson vs Spearman.

#### 11. CU-11: Serie de Tiempo y Detección de Fechas Atípicas de Asientos Manuales ($Z$-Score)
- **Manejo de Data:** Agregación del volumen diario de asientos manuales (`ORIGEN_ASIENTO = 'MANUAL'`) y cálculo del Z-Score diario:
  $$Z_t = \frac{V_t - \mu_V}{\sigma_V}$$
- **Visualización:** Gráfico temporal resaltando picos anómalos con $Z_t \ge 2.5$.

#### 12. CU-12: Comparativa de Distribución Paramétrica vs No-Paramétrica ($\mu$ vs $\tilde{x}$, $\sigma$ vs $\text{IQR}$)
- **Manejo de Data:** Evaluación del sesgo (*Skewness*) comparando Media ($\mu$) vs Mediana ($\tilde{x}$) y StdDev ($\sigma$) vs IQR.
- **Visualización:** Diagrama de caja y bigotes (Tukey $1.5 \times \text{IQR}$) etiquetando importes atípicos.

---

### 🔹 SECCIÓN C: DASHBOARD EJECUTIVO SOX Y EVIDENCIA FORENSE

#### 13. CU-13: Cuantificación Monetaria ($) de Violaciones de Segregación de Funciones (SoD)
- **Manejo de Data:** Filtrado y suma monetaria total de asientos donde $\text{USUARIO\_REGISTRADOR} == \text{USUARIO\_APROBADOR}$.
- **Visualización:** Tarjeta KPI de impacto financiero ($) con desglose de usuarios infractores.

#### 14. CU-14: Cuantificación Monetaria ($) de Aprobaciones Neón (< 60s) y Montos Redondos Elevados
- **Manejo de Data:** Filtrado de registros con `DIFERENCIA_SEGUNDOS < 60` e importes terminados en `.00` superiores a $100,000.
- **Visualización:** Alerta monetaria por aprobaciones exprés y montos cerrados.

#### 15. CU-15: Exportación de Expediente de Evidencia Forense con Sello SHA-256
- **Manejo de Data:** Consolidación de evidencias de auditoría en un expediente inmutable.
- **Visualización:** Exportación del dictamen de auditoría en PDF/CSV firmado digitalmente con hash SHA-256.

---

## 📅 ASIGNACIÓN DE CASOS DE USO A LAS 5 FASES

| Fase | Título | Casos de Uso Asignados |
| :--- | :--- | :--- |
| **Fase 1** | Motor AST & Expresiones de Fechas | **CU-01, CU-02, CU-03, CU-04** |
| **Fase 2** | Canvas Visual de Esquema Plata | **CU-05, CU-06, CU-10** |
| **Fase 3** | Linaje y Persistencia | **CU-07, CU-08** |
| **Fase 4** | Pearson, Spearman & Z-Score (Oro) | **CU-09, CU-11, CU-12, CU-13, CU-14** |
| **Fase 5** | Command Center SOX ($) | **CU-15, CU-16, CU-17** |
