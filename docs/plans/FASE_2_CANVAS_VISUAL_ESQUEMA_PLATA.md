# 🎨 PLAN DE IMPLEMENTACIÓN - FASE 2
## Constructor Dinámico de Esquema, Canvas Visual, Diagnosticador de Fechas & Splitter de Montos (Frontend Vue3 / TS)
**Proyecto de Maestría en Analítica de Datos | Stack: Vue 3 (Composition API), TypeScript, Pinia**

---

## 🎯 OBJETIVO DE LA FASE 2
Desarrollar la interfaz visual interactiva (*Data Pipeline Builder / Schema Canvas*) donde el auditor:
1. Ve la matriz de coincidencia en % entre fechas para tomar una decisión fundada sobre si conserva 1 o 3 fechas.
2. Configura la separación o unificación de columnas de **Cargos (Débitos)** y **Abonos (Créditos)**.
3. Reordena, selecciona y compila dinámicamente las columnas de la Capa Plata.

---

## 📐 CASOS DE USO ASOCIADOS

### CU-18: Diagnosticador Visual de Redundancia Temporal de Fechas
- **Descripción:** El Canvas muestra un badge informativo sobre el pareo de fechas:  
  *“`FECHA_REGISTRO` vs `FECHA_POSTEO`: 100% idénticas. ¿Deseas descartar la segunda fecha o conservar ambas?”*

### CU-19: Transformador & Separador Atómico de Cargos y Abonos
- **Descripción:** Control selector interactivo para dividir 1 columna signada en `CARGO` / `ABONO` o mantener 2 columnas independientes.

### CU-06: Selección, Reordenamiento y Reducción Dinámica de Campos (Schema Builder Canvas)
- **Descripción:** Reducción interactiva de $N$ columnas crudas a $M$ columnas canónicas.

---

## 🛠️ ESTRUCTURA Y ARCHIVOS A CREAR (< 200 LÍNEAS POR ARCHIVO)

### 1. `frontend/src/components/forms/SilverSchemaCanvas.vue`
- Interfaz del canvas interactivo con el indicador de coincidencia de fechas y selector de split de cargos/abonos.

### 2. `frontend/src/composables/useSilverSchemaBuilder.ts`
- Composable con reactividad TypeScript para manejar el estado del pareo de fechas y split de importes.

### 3. `frontend/src/types/schema_canvas.ts`
- Interfaces TypeScript (`DateRedundancyReport`, `AmountSplitterConfig`).

---

## 🧪 CRITERIOS DE ACEPTACIÓN Y VERIFICACIÓN
1. Compilación TypeScript `npx vue-tsc --noEmit` limpia con 0 errores.
2. Visualización reactiva del % de coincidencia entre fechas en el Canvas.
3. Ningún archivo supera las 200 líneas.
