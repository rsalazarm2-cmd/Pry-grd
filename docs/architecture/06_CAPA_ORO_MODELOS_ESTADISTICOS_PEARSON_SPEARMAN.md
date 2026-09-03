# 🥇 06. CAPA ORO: MODELADO ESTADÍSTICO Y ANÁLISIS DE ATÍPICOS
### Pearson, Spearman, Mahalanobis D², Z-Score Temporal & Comparativa Paramétrica
**Proyecto de Maestría en Analítica de Datos | Stack: DuckDB Vectorizado, Python, Chart.js**

---

## 📌 1. RESPONSABILIDAD DE LA CAPA ORO

La Capa Oro transforma la data purificada de Plata en **Data Marts Analíticos** y aplica modelos estadísticos avanzados de alto nivel para respaldar la auditoría forense con rigor científico.

---

## 📐 2. ESPECIFICACIÓN DETALLADA DE MODELOS MATEMÁTICOS

### 1. Matriz de Correlación Lineal de Pearson ($r$)
Medición de la dependencia lineal continua entre las variables financieras numéricas:
$$r_{X,Y} = \frac{\sum_{i=1}^n (X_i - \bar{X})(Y_i - \bar{Y})}{\sqrt{\sum_{i=1}^n (X_i - \bar{X})^2 \sum_{i=1}^n (Y_i - \bar{Y})^2}}$$
*Rango:* $r \in [-1.0, 1.0]$. Cómputo vectorizado directo en DuckDB sobre `CARGO_MONEDA_FUNCIONAL`, `ABONO_MONEDA_FUNCIONAL`, `TASA_CAMBIO` y `LINEA_ASIENTO`.

### 2. Matriz de Correlación de Rangos de Spearman ($\rho$)
Medición no paramétrica de dependencias monótonas resistente a importes financieros extremos (*outliers*):
$$\rho = 1 - \frac{6 \sum_{i=1}^n d_i^2}{n(n^2 - 1)}$$
donde $d_i = \text{rg}(X_i) - \text{rg}(Y_i)$ es la diferencia entre los rangos asignados a las observaciones.

### 3. Distancia Multivariada de Mahalanobis ($D^2$)
Detección de observaciones anómalas considerando la covarianza entre múltiples variables (Monto, Tasa Cambio, Líneas):
$$D^2(x) = (x - \mu)^T \Sigma^{-1} (x - \mu)$$
donde $\mu$ es el vector de medias y $\Sigma$ es la matriz de covarianza. Identifica asientos cuyo comportamiento combinado es sospechoso aunque sus variables individuales parezcan normales.

### 4. Serie de Tiempo y Detección Z-Score de Fechas Atípicas
Cómputo del volumen diario $V_t$ de asientos manuales (`ORIGEN_ASIENTO = 'MANUAL'`) y su desviación estandarizada:
$$Z_t = \frac{V_t - \mu_V}{\sigma_V}$$
Una fecha se clasifica como **Atípica Contable** si $Z_t \ge 2.5$ o si se contabilizó en fin de semana.

### 5. Comparativa Paramétrica vs No-Paramétrica (Tukey IQR & Skewness)
- Media ($\mu$) vs Mediana ($\tilde{x}$) para evaluar asimetría (*Skewness*).
- Desviación Estandar ($\sigma$) vs Rango Intercuartílico ($\text{IQR} = Q_3 - Q_1$).
- **Límites de Atípicos de Tukey:**
  $$\text{Límite Inferior} = Q_1 - 1.5 \times \text{IQR}$$
  $$\text{Límite Superior} = Q_3 + 1.5 \times \text{IQR}$$
