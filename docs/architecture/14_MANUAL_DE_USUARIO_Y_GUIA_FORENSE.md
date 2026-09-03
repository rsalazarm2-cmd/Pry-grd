# 👤 14. MANUAL DE USUARIO Y GUÍA DE AUDITORÍA FORENSE
### Flujo de Trabajo Operativo para Auditores Financieros y Analistas Contables
**Proyecto de Maestría en Analítica de Datos | Enfoque: SOX 404 & Auditoría Externa**

---

## 📌 1. FLUJO OPERATIVO END-TO-END DEL AUDITOR

El manual de usuario guía al auditor paso a paso a través de las cuatro capas de la plataforma:

```
[ Step 1: Carga de Dataset ] ➔ [ Step 2: Schema Canvas Plata ] ➔ [ Step 3: Modelos Oro ] ➔ [ Step 4: Command Center SOX ]
```

---

## 📋 2. PASOS OPERATIVOS DETALLADOS

### Paso 1: Ingesta de Extracto Contable ERP (Capa Bronce)
1. Abrir el menú hamburguesa `☰` en el frontend web.
2. Hacer clic en **`+ Cargar Data`** y seleccionar el archivo CSV o Parquet exportado de Oracle EBS, SAP S/4HANA o MS Dynamics.
3. El sistema calcula la firma **SHA-256 de Custodia Digital** y genera el perfil exploratorio crudo (EDA) mostrando % de nulos y estadísticas.

### Paso 2: Estandarización y Schema Canvas (Capa Plata)
1. El auditor navega a la **Capa Plata**.
2. Organiza y mapea las columnas de origen hacia la **Taxonomía Canónica de 33 Campos en Español**.
3. Aplica la transformación de **Amount Splitter** (+/- ➔ Cargo/Abono) y configura las expresiones AST de fechas (deltas y días de la semana).
4. Al hacer clic en **Compilar Esquema**, el sistema guarda la memoria de reglas en `.column_mapping_rules.json` (1 ms).

### Paso 3: Análisis Estadístico y Detección de Anomalías (Capa Oro)
1. Visualización de las matrices de correlación de **Pearson ($r$)** y **Spearman ($\rho$)**.
2. Identificación de asientos manuales atípicos en la serie de tiempo **Z-Score ($Z_t \ge 2.5$)**.
3. Evaluación de la Ley de Benford (MAD) y Entropía de Shannon en descripciones.

### Paso 4: Command Center SOX y Evidencia Forense
1. Revisión de los KPIs de impacto monetario en dólares ($) para SoD Maker-Checker y Aprobaciones Neón (< 60s).
2. Exportación del expediente final de evidencia firmado digitalmente con hash SHA-256.
