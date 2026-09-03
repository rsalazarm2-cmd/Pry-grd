# 📊 PLAN DE IMPLEMENTACIÓN - FASE 4
## Modelado Estadístico Avanzado de Maestría (Pearson, Spearman y Z-Score en Capa Oro)
**Proyecto de Maestría en Analítica de Datos | Stack: DuckDB Vectorizado, Python Ninja API, Vue 3**

---

## 🎯 OBJETIVO DE LA FASE 4
Desarrollar el motor estadístico de alto nivel en la Capa Oro para evaluar la salud contable con modelos matemáticos y probabilísticos probados.

---

## 📐 CASOS DE USO ASOCIADOS & MARCO MATEMÁTICO

### CU-11: Matriz de Correlación Lineal de Pearson ($r$) en DuckDB Vectorizado
- **Fórmula:**
  $$r_{X,Y} = \frac{\sum (X_i - \bar{X})(Y_i - \bar{Y})}{\sqrt{\sum (X_i - \bar{X})^2 \sum (Y_i - \bar{Y})^2}}$$
- **Aplicación:** Medición de la dependencia entre `CARGO_MONEDA_FUNCIONAL`, `ABONO_MONEDA_FUNCIONAL`, `TASA_CAMBIO` y `LINEA_ASIENTO`.

### CU-12: Matriz de Correlación de Rangos de Spearman ($\rho$) para Distribuciones Sesgadas
- **Fórmula:**
  $$\rho = 1 - \frac{6 \sum d_i^2}{n(n^2 - 1)}$$
- **Aplicación:** Evaluación de correlaciones monótonas no lineales resistentes a outliers extremos.

### CU-13: Detección Temporal de Fechas Atípicas mediante Algoritmo Z-Score ($Z_t \ge 2.5$)
- **Fórmula:**
  $$Z_t = \frac{V_t - \mu_V}{\sigma_V}$$
- **Aplicación:** Identificación de picos anómalos de posteo en asientos manuales (`ORIGEN_ASIENTO = 'MANUAL'`).

### CU-14: Evaluación de Distribución Paramétrica vs No-Paramétrica ($\mu$ vs $\tilde{x}$, $\sigma$ vs $\text{IQR}$)
- **Aplicación:** Comparativa de Media vs Mediana y límites de Tukey ($1.5 \times \text{IQR}$) para caracterizar la asimetría (*Skewness*) de los importes contables.

---

## 🛠️ ESTRUCTURA Y ARCHIVOS A CREAR (< 200 LÍNEAS POR ARCHIVO)

### 1. `backend/src/gold/infrastructure/gold_analytics_engine.py`
- Consultas SQL DuckDB vectorizadas para Pearson, Spearman, Z-Score y Tukey IQR.

### 2. `backend/src/gold/api/gold_analytics_router.py`
- API REST Ninja con endpoints `@router.get("/correlations")`, `@router.get("/date-anomalies")`.

### 3. `frontend/src/views/GoldWorkspace.vue`
- Workspace interactivo con mapas de calor de correlaciones y serie de tiempo de fechas atípicas.

---

## 🧪 CRITERIOS DE ACEPTACIÓN Y VERIFICACIÓN
1. Valores de Pearson $r$ y Spearman $\rho$ validados numéricamente entre $-1.0$ y $+1.0$.
2. Z-Score temporal identificando con precisión picos de volumen atípicos.
3. `npx vue-tsc --noEmit` sin errores.
