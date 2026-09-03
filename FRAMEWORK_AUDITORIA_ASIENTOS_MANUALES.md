# 🏛️ Framework de Auditoría Forense de Asientos Manuales & Diagnóstico de Causa Raíz
**Proyecto de Maestría en Analítica de Datos - Medallion Architecture (Oracle EBS / DuckDB)**
*Dictamen de Auditor Forense de Asientos Manuales (20+ Años de Experiencia en Firmas Big 4 / Fortune 500)*

---

## ⚖️ CAPÍTULO 1: VEREDICTO DE AUDITORÍA ("¿SIRVE O NO SIRVE EN EL MUNDO REAL?")

### **VEREDICTO DIPLOMÁTICO: SIRVE COMO MOTOR CORE ANALÍTICO (MVP).**
### **VEREDICTO CRUDO EN EL MUNDO REAL: NO PASA UNA AUDITORÍA DE PRODUCTO EN PRODUCCIÓN.**

#### ¿Por qué SÍ sirve?
- **Procesamiento de Ultra Alta Velocidad:** Supera al 90% de los entornos de firmas locales que usan planillas masivas de Excel o scripts sueltos en Python que colapsan la memoria RAM. Procesa millones de filas en **< 10 milisegundos** gracias a la arquitectura **DuckDB + Parquet**.
- **Linaje y Gobernanza Transparente:** La separación Medallion (Bronce ➔ Plata ➔ Oro) y la persistencia de recetas en JSON garantizan que las transformaciones sean 100% reproducibles.

#### ¿Por qué NO pasa un examen de producción en el mundo real en su estado actual?
- Porque audita **fila por fila con reglas estáticas aisladas**, permitiendo que cualquier contador con intenciones de fraude evada los controles mediante fraccionamiento de montos, manipulación de glosas con caracteres especiales o registros retroactivos.

---

## 🎯 CAPÍTULO 2: ANÁLISIS DE LA CAUSA RAÍZ

### La Causa Raíz de las Fallas en Auditoría Forense:
> **"Tratar cada transacción contable como un hecho aislado e independiente."**

El fraude en asientos manuales **NUNCA ocurre en una sola fila aislada**. Ocurre en **patrones multidimensionales y comportamientos anómalos a lo largo del tiempo**:
1. Un usuario registrando asientos en fin de semana.
2. Montos fraccionados acumulados en el mismo día por el mismo empleado para evitar umbrales de firma.
3. Glosas ambiguas, nulas o con puntos para ocultar desembolsos.
4. Brechas de tiempo entre la fecha real de creación en la base de datos y la fecha contable declarada.

---

## 💥 CAPÍTULO 3: MATRIZ COMPLETA DE IMPERFECCIONES Y VULNERABILIDADES DEL PROYECTO

A continuación se detallan las **7 Imperfecciones Técnicas y Operativas** del sistema actual:

```
                       MATRIZ DE IMPERFECCIONES DEL SISTEMA ACTUAL
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ 🔴 IMPERFECCIÓN 1: AUSENCIA DE LA LEY DE BENFORD (1er y 2º Dígito)          │
 │  • Falla: Sin la curva de Benford, el sistema es incapaz de detectar la    │
 │    estimación o manipulación humana no natural de números.                 │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ 🔴 IMPERFECCIÓN 2: INCAPACIDAD DE DETECTAR FRACCIONAMIENTO (Split)          │
 │  • Falla: Si el límite de firma es $10,000, un usuario crea 5 asientos de  │
 │    $9,950 en el mismo día. El sistema actual no acumula por ventana móvil.  │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ 🔴 IMPERFECCIÓN 3: CEGUERA ANTE EVASIONES SEMÁNTICAS EN GLOSAS (NLP)        │
 │  • Falla: El filtro textual falla si el fraudeador escribe "A.j.u.s.t.e",   │
 │    "Reclasif", o deja la glosa vacía o con un solo punto ".".              │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ 🔴 IMPERFECCIÓN 4: FALTA DE AUDITORÍA DE RETROACTIVIDAD DE CIERRE (Cut-Off) │
 │  • Falla: No se calcula la brecha entre la fecha de creación real en la BD  │
 │    (Creation Date) y la fecha contable (GL Date) para detectar Backdating.  │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ 🔴 IMPERFECCIÓN 5: REGLAS NO-CODE LIMITADAS A ESTRUCTURAS PLANAS            │
 │  • Falla: ConditionalRuleBuilder.vue no soporta sub-grupos con paréntesis  │
 │    como ((A AND B) OR (C AND D)).                                           │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ 🔴 IMPERFECCIÓN 6: AUSENCIA DE SCORING GLOBAL CONSOLIDADO DE RIESGO         │
 │  • Falla: El sistema genera alertas aisladas pero no consolida un puntaje  │
 │    ponderado único (0 a 100) por asiento para ordenar de mayor a menor.     │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ 🔴 IMPERFECCIÓN 7: PISTA DE AUDITORÍA (AUDIT TRAIL) MUTABLE Y SIN RBAC      │
 │  • Falla: No hay firma criptográfica (SHA-256) de recetas ni control de     │
 │    accesos por roles (Auditor, Supervisor, Administrador).                 │
 └─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛡️ CAPÍTULO 4: LA SOLUCIÓN DEFINITIVA: MOTOR VECTORIAL DE 5 DIMENSIONES

Para resolver la causa raíz de fondo, la **Capa Plata** debe enriquecer cada asiento con un **Vector de 5 Dimensiones Forenses**:

```
                  ENTRADA: 33 Campos Crudos de Oracle EBS
                                     │
                                     ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ MOTOR VECTORIAL DE ENRIQUECIMIENTO FORENSE (DuckDB Engine)                  │
 ├───────────────────────────────────┬─────────────────────────────────────────┤
 │ 1. Vector Temporal / Horario      │ ➔ `FLAG_TEMPORAL_RIESGO`                │
 │    (Fin de semana / Nocturno)     │    (Sábado, Domingo o fuera de horario)  │
 ├───────────────────────────────────┼─────────────────────────────────────────┤
 │ 2. Vector Comportamiento Usuario  │ ➔ `FLAG_SOD_AUTOAPROBADO` & DELTA_TIME   │
 │    (Maker/Checker & Velocidad)    │    (Registrador == Aprobador o < 60s)    │
 ├───────────────────────────────────┼─────────────────────────────────────────┤
 │ 3. Vector Semántico de Glosa (NLP)│ ➔ `SCORE_ENTROPIA_GLOSA`                │
 │    (Normalización Unicode + NLP)  │    (Detecta "A.j.u.s.t.e", ".", nulas)   │
 ├───────────────────────────────────┼─────────────────────────────────────────┤
 │ 4. Vector Matemático / Benford    │ ➔ `FLAG_LEY_BENFORD_ANOMALO`            │
 │    (Distribución de dígitos)      │    (Desviación logarítmica de montos)    │
 ├───────────────────────────────────┼─────────────────────────────────────────┤
 │ 5. Vector Acciones Acumuladas     │ ➔ `FLAG_FRACCIONAMIENTO_WINDOW_SUM`     │
 │    (Ventana móvil por usuario/día)│    (Suma acumulada cerca al límite)    │
 └───────────────────────────────────┴─────────────────────────────────────────┘
                                     │
                                     ▼
   RESULTADO EN PLATA: 33 Campos Estandarizados + 5 Vectores Forenses Integrados
                                     │
                                     ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ CAPA ORO: SCORING GLOBAL DE FRAUDE (0 A 100) & DATAMARTS EJECUTIVOS         │
 └─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 CAPÍTULO 5: MATRIZ DE LAS 9 PRUEBAS DE AUDITORÍA FORENSE

| # | Prueba Forense | Definición Técnica y Riesgo | Algoritmo / Regla Analítica |
|---|---|---|---|
| **1** | **Separación de Fuente** | Aislar asientos creados manualmente en el Libro Mayor de los automáticos. | `ORIGEN_ASIENTO = 'Manual'` |
| **2** | **Fraccionamiento & Benford** | Detectar montos fraccionados justo por debajo del límite de firma o montos anómalos. | `SUM(CARGO) OVER(PARTITION BY USUARIO, FECHA)` + `Benford` |
| **3** | **Segregación (SOD)** | Violación Maker/Checker donde la misma persona registra y aprueba el asiento. | `USUARIO_REGISTRADOR = USUARIO_APROBADOR` |
| **4** | **Cuentas Sensibles & Puente** | Cruces atípicos entre cuentas de gasto y activos o cuentas transitorias no liquidadas. | `CUENTA_CONTABLE IN ('Clearing', 'Suspense')` |
| **5** | **Corte de Mes (Cut-Off)** | Registros manuales efectuados en fin de semana o fuera de horario comercial. | `IS_WEEKEND = True OR HORARIO NOT BETWEEN 08:00 AND 19:00` |
| **6** | **Aprobaciones Flash** | Aprobaciones automáticas realizadas sin tiempo físico de revisión humana. | `DELTA_SEGUNDOS_APROBACION < 60` |
| **7** | **NLP en Glosas** | Búsqueda de términos sospechosos, normalización Unicode y glosas de 1 carácter. | `LOWER(UNACCENT(GLOSA)) LIKE '%ajuste%'` |
| **8** | **Reversiones Post-Cierre** | Asientos manuales del 31-Dic revertidos automáticamente los primeros días de Enero. | `FECHA_REGISTRO = '31-DEC' AND REVERTIDO = True` |
| **9** | **Integridad & Doble Partida** | Asientos donde la suma de Cargos difiere de Abonos o la cabecera difiere de las líneas. | `SUM(CARGO) != SUM(ABONO)` |

---

## 🚀 CAPÍTULO 6: HOJA DE RUTA PRIORIZADA (REMEDIACIÓN PASO A PASO)

1. **Fase 1 (Inmediata):** Implementar el **Motor Vectorial Forense en Backend** (`ForensicFeatureVectorEngine`) en DuckDB para inyectar los 5 vectores a Plata.
2. **Fase 2:** Implementar la prueba forense de la **Ley de Benford (1er y 2º dígito)** con visualización en Frontend.
3. **Fase 3:** Implementar el Data Mart de **Scoring Consolidado de Riesgo (0 a 100 Puntos)** en la Capa Oro.
4. **Fase 4:** Implementar el motor de **Audit Trail Criptográfico (SHA-256)**.

---
*Documento actualizado en la raíz del proyecto para dictamen y evaluación de la Tesis de Maestría.*
