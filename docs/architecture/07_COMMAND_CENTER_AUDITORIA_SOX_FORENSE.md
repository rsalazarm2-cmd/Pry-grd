# 🛡️ 07. COMMAND CENTER DE AUDITORÍA SOX Y CONTROL INTERNO
### Evaluación de Impacto Monetario ($), Segregación de Funciones, Smurfing & Custodia Digital
**Proyecto de Maestría en Analítica de Datos | Stack: Vue 3, Pinia, Python Ninja API, DuckDB**

---

## 📌 1. PROPÓSITO DEL COMMAND CENTER DE AUDITORÍA

Proporcionar al auditor financiero, revisor SOX 404 y socio de auditoría un **cuadro de mando ejecutivo unificado enfocado en la cuantificación del riesgo financiero en dólares ($)** y la identificación de fallos en la estructura de control interno.

---

## 📐 2. ESPECIFICACIÓN DETALLADA DE INDICADORES Y DETECTORES FORENSES

### 1. Riesgo por Violación de Segregación de Funciones (SoD Maker-Checker)
- **Fórmula de Exposición Monetaria ($):**
  $$\text{Impacto SoD (\$)} = \sum \text{CARGO\_MONEDA\_FUNCIONAL} \quad \text{donde } \text{USUARIO\_REGISTRADOR} == \text{USUARIO\_APROBADOR}$$
- **Propósito:** Cuantificar el dinero que circuló por el sistema donde la misma persona creó y autorizó el asiento manual en el ERP.

---

### 2. Detector de Aprobación Neón (< 60 segundos)
- **Fórmula de Exposición Monetaria ($):**
  $$\text{Impacto Aprobación Neón (\$)} = \sum \text{CARGO} \quad \text{donde } \text{DIFERENCIA\_SEGUNDOS\_APROBACION} < 60$$
- **Propósito:** Cuantificar posteos que se aprobaron en segundos sin posibilidad física de revisión humana de soporte documental.

---

### 3. Asientos Contabilizados en Fin de Semana
- **Fórmula de Exposición Monetaria ($):**
  $$\text{Impacto Fin de Semana (\$)} = \sum \text{CARGO} \quad \text{donde } \text{DIA\_SEMANA} \in (\text{'SÁBADO'}, \text{'DOMINGO'})$$
- **Propósito:** Aislar transacciones registradas fuera de la jornada laboral oficial de la compañía.

---

### 4. Detector de Smurfing (Splitting / Fraccionamiento de Asientos)
- **Patrón Forense:** Cuando una política de control interno exige aprobación especial para asientos mayores a $10,000, los infractores fraccionan el monto creando múltiples asientos el mismo día por **$9,999 o $9,500**.
- **Algoritmo SQL Vectorizado:**
  ```sql
  SELECT 
      USUARIO_REGISTRADOR,
      FECHA_CONTABILIZACION,
      COUNT(*) AS total_asientos_fraccionados,
      SUM(CARGO_MONEDA_FUNCIONAL) AS monto_total_fraccionado
  FROM read_parquet('silver.parquet')
  WHERE CARGO_MONEDA_FUNCIONAL BETWEEN 9000 AND 9999.99
  GROUP BY USUARIO_REGISTRADOR, FECHA_CONTABILIZACION
  HAVING COUNT(*) >= 2;
  ```

---

### 5. Expediente de Evidencia Forense con Sello Digital SHA-256
- Generación de un informe final de auditoría exportable en PDF y CSV.
- Cada expediente incluye el sello criptográfico SHA-256 inmutable de la fuente y de los resultados para servir como **evidencia legal en procesos de auditoría externa o litigio**.
