# 🧬 PLAN DE IMPLEMENTACIÓN - FASE 3
## Motor de Trazabilidad, Linaje Inmutable y Persistencia (.column_mapping_rules.json)
**Proyecto de Maestría en Analítica de Datos | Stack: Python, JSON Schema, Vue 3, Pinia**

---

## 🎯 OBJETIVO DE LA FASE 3
Garantizar la auditabilidad y memoria contable del sistema mediante la matriz transparente de linaje (*Data Lineage*) y la persistencia inmutable de recetas contables en `.column_mapping_rules.json`.

---

## 📐 CASOS DE USO ASOCIADOS

### CU-07: Trazabilidad y Linaje Transparente de Mapeo (Data Lineage)
- **Descripción:** Visualizar el flujo claro `Columna Origen (Bronce)` ➔ `Columna Plata`.
- **Flujo:**  
  1. El sistema renderiza la tabla de linaje con badges de color.
  2. Muestra el nombre original, el tipo inferido, la regla de transformación (ej. categorización) y la columna destino.
- **Resultado:** Auditabilidad 100% transparente para firmas revisoras SOX.

### CU-08: Persistencia Inmutable de la Receta Contable (`.column_mapping_rules.json`)
- **Descripción:** Almacenar la receta personalizada del auditor en disco.
- **Flujo:**  
  1. Al ejecutar la limpieza, se escribe `data/projects/{project_id}/.column_mapping_rules.json`.
  2. En cargas futuras con la misma estructura de columnas, el sistema carga el manifiesto en **1 ms** omitiendo el modelo NLP.
- **Resultado:** Cero reprocesamiento inútil de IA en descargas mensuales recurrentes.

### CU-03: Carga Incremental Multifuente y Reutilización de Manifiestos
- **Descripción:** Detección automática de hash de esquema para re-aplicar manifiestos.

---

## 🛠️ ESTRUCTURA Y ARCHIVOS A CREAR (< 200 LÍNEAS POR ARCHIVO)

### 1. `frontend/src/components/analytics/SilverLineageTable.vue`
- Tabla visual de linaje interactiva con indicadores cromáticos.

### 2. `backend/src/bronze/infrastructure/mapping_rules_persistence_service.py`
- Gestor inmutable de lectura/escritura JSON de reglas de mapeo por proyecto.

---

## 🧪 CRITERIOS DE ACEPTACIÓN Y VERIFICACIÓN
1. Verificación de carga en 1 ms al re-solicitar sugerencias de mapeo con un `.column_mapping_rules.json` existente.
2. `npx vue-tsc --noEmit` sin errores.
