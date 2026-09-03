# 🛡️ PLAN DE IMPLEMENTACIÓN - FASE 5
## Command Center Ejecutivo de Auditoría SOX & Control Interno (KPIs Monetarios $)
**Proyecto de Maestría en Analítica de Datos | Stack: Vue 3, Chart.js / Canvas, Python Ninja API**

---

## 🎯 OBJETIVO DE LA FASE 5
Unificar toda la evidencia contable en un tablero ejecutivo enfocado en el impacto monetario real ($) por fallos de control interno, segregación de funciones e integridad financiera.

---

## 📐 CASOS DE USO ASOCIADOS

### CU-15: Evaluación de Impacto Monetario ($) por Violación de Segregación de Funciones (SoD)
- **Descripción:** Suma en dólares/moneda local de asientos donde `USUARIO_REGISTRADOR == USUARIO_APROBADOR`.
- **Resultado:** Indicador clave de exposición en auditorías SOX 404.

### CU-16: Detección de Posteo Neón (< 60s) y Montos Redondos Elevados ($)
- **Descripción:** Cuantificación monetaria de aprobaciones ultra-rápidas e importes terminados en `.00`.

### CU-17: Exportación de Evidencia Forense Digital Firmada con Hash SHA-256
- **Descripción:** Generación de informes en PDF/CSV firmados digitalmente para cadena de custodia.

---

## 🛠️ ESTRUCTURA Y ARCHIVOS A CREAR (< 200 LÍNEAS POR ARCHIVO)

### 1. `frontend/src/views/AuditWorkspace.vue`
- Command Center ejecutivo con tarjetas de riesgo monetario ($) y gráficos interactivos.

### 2. `backend/src/audit/infrastructure/forensic_audit_service.py`
- Servicio backend para consolidar métricas de riesgo monetario SOX.

---

## 🧪 CRITERIOS DE ACEPTACIÓN Y VERIFICACIÓN
1. Exposición monetaria ($) calculada con precisión matemática sin truncar decimales.
2. `npx vue-tsc --noEmit` en verde (0 errores).
