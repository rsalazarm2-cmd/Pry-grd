# 🏛️ PLAN MAESTRO DE SUPERPODERES Y COMPLEJIDAD FORENSE (5 FASES)
### Sistema de Auditoría Forense Financiera & Arquitectura Medallion (Bronce, Plata, Oro)
**Maestría en Analítica de Datos | Stack: DuckDB Nativo, Python/Django, Vue 3/TypeScript**

---

## 💥 ANÁLISIS DE COMPLEJIDAD Y SUPERPODERES DEL AUDITOR POR FASE

---

### 📌 FASE 1: Motor AST, Ley de Benford, Entropía de Shannon & Separador de Partida Doble
**Nivel de Complejidad: Alto (Cómputo Estadístico-Vectorizado en DuckDB)**

#### 🚀 Superpoderes Integrados:
1. **Prueba de Ley de Benford (First & First-Two Digits Test):**
   - Evaluación matemática de la frecuencia del primer dígito $P(d) = \log_{10}(1 + \frac{1}{d})$ y cálculo de la **Desviación Absoluta Media (MAD)** sobre montos para detectar manipulación o invención de números.
2. **Entropía de Información de Shannon ($H(X)$):**
   - Cálculo de la entropía $H(X) = -\sum P(x) \log_2 P(x)$ sobre descripciones y glosas para aislar texto aleatorio o descripciones repetitivas vacías.
3. **Cómputo AST de Fechas & Matriz de Redundancia %:**
   - Evaluador vectorizado `DATEDIFF` (segundos/días), detección de fin de semana y diagnóstico de % de coincidencia exacta entre pares de fechas.
4. **Amount Splitter Engine (Cargos / Abonos):**
   - Transformador para separar 1 columna signada (+/-) en `CARGO` y `ABONO` o fragmentar la base en 2 vistas independientes.

---

### 🎨 FASE 2: Canvas Visual Interactivo, Reglas Condicionales No-Code & Schema Builder
**Nivel de Complejidad: Alto (Engine de Pipeline Visual & UI Reactiva)**

#### 🚀 Superpoderes Integrados:
1. **Reglas de Transformación Condicional `IF-THEN-ELSE` No-Code:**
   - Evaluador dinámico donde el auditor define reglas (ej. `IF MONTO > 100000 AND DIA_SEMANA IN ('SÁBADO','DOMINGO') THEN RIESGO = 'CRÍTICO'`).
2. **Organizador Visual de Esquema (Schema Blueprint Canvas):**
   - Drag-and-drop para reordenar columnas, renombrar tipos de datos, aplicar imputaciones avanzadas y previsualizar la tabla Plata antes de compilar.
3. **Diagnosticador de Redundancia de Fechas en Vivo:**
   - Indicador neón que alerta la coincidencia % entre fechas y permite descartar redundancias con 1 clic.

---

### 🧬 FASE 3: Motor de Trazabilidad, Linaje Inmutable y Grafo de Metadatos (.column_mapping_rules)
**Nivel de Complejidad: Medio-Alto (Persistencia & Memoria Criptográfica)**

#### 🚀 Superpoderes Integrados:
1. **Grafo y Matriz de Linaje de Metadatos (Data Lineage):**
   - Visualización del flujo transparente `Origen (Bronce)` ➔ `Transformaciones` ➔ `Destino (Plata)`.
2. **Persistencia Criptográfica en 1 ms (`.column_mapping_rules.json`):**
   - Almacenamiento local del manifiesto de mapeo con hash SHA-256 para recargar reglas en 1 ms en descargas mensuales recurrentes.

---

### 📊 FASE 4: Modelado Estadístico Avanzado (Pearson, Spearman, Mahalanobis & Time Series Z-Score)
**Nivel de Complejidad: Muy Alto (Estadística Multivariada & Series Temporales)**

#### 🚀 Superpoderes Integrados:
1. **Matrices de Correlación Matemáticas (Pearson $r$ & Spearman $\rho$):**
   - Evaluación vectorizada en DuckDB de dependencias lineales y monótonas de rangos entre todas las variables continuas.
2. **Distancia Multivariada de Mahalanobis ($D^2$):**
   - Algoritmo para detectar anomalías en la combinación (Monto, Tasa Cambio, Líneas) que no se ven aisladamente en 1 sola variable.
3. **Serie de Tiempo y Detección de Fechas Atípicas ($Z$-Score):**
   - Algoritmo $Z_t = \frac{V_t - \mu_V}{\sigma_V}$ sobre el volumen diario de asientos manuales (`ORIGEN_ASIENTO = 'MANUAL'`).
4. **Comparativa Paramétrica vs No-Paramétrica (Tukey IQR & Skewness):**
   - Media ($\mu$) vs Mediana ($\tilde{x}$), StdDev ($\sigma$) vs IQR y límites de Tukey ($1.5 \times \text{IQR}$).

---

### 🛡️ FASE 5: Command Center SOX, Grafo de Segregación de Funciones & Detectores de Smurfing
**Nivel de Complejidad: Muy Alto (Auditoría Forense SOX & Evidencia Inviolable)**

#### 🚀 Superpoderes Integrados:
1. **Grafo de Relaciones Maker-Checker (SoD Graph):**
   - Mapeo de red entre `USUARIO_REGISTRADOR` y `USUARIO_APROBADOR` para descubrir colusión con monto cuantificado en dólares ($).
2. **Detector de Fragmentación de Montos (Smurfing / Splitting):**
   - Identificación de múltiples asientos creados el mismo día por $9,999 para evadir el umbral de aprobación de $10,000.
3. **Posteo Exprés (< 60s) & Montos Redondos Elevados ($):**
   - Cuantificación en dólares de aprobaciones exprés e importes terminados en `.00`.
4. **Expediente de Evidencia Forense con Sello SHA-256:**
   - Exportación de expedientes PDF/CSV firmados digitalmente para auditorías SOX 404 / externas.

---

## 📅 MATRIZ DE RESUMEN DE SUPERPODERES POR FASE

| Fase | Título | Superpoderes Principales | Nivel Complejidad |
| :--- | :--- | :--- | :---: |
| **Fase 1** | Motor AST, Benford & Shannon | Ley de Benford, Entropía Shannon, Deltas Fechas, Amount Splitter | **Alto** |
| **Fase 2** | Canvas Visual & Reglas `IF-THEN` | Reglas Condicionales No-Code, Schema Canvas, Redundancia Fechas | **Alto** |
| **Fase 3** | Linaje Transparente & Memoria | Grafo Linaje Origen-Plata, Persistencia SHA-256 en 1 ms | **Medio-Alto** |
| **Fase 4** | Pearson, Spearman & Mahalanobis | Correlaciones r/ρ, Mahalanobis $D^2$, Z-Score temporal, Tukey IQR | **Muy Alto** |
| **Fase 5** | Command Center SOX & Smurfing | Grafo SoD Maker-Checker, Detector Smurfing, Hash SHA-256 | **Muy Alto** |
