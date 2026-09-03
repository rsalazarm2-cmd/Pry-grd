# 📊 15. MATRIZ DE TRAZABILIDAD Y AFIRMACIONES DE AUDITORÍA (SOX 404 / ISA 315)
### Mapeo entre Estándares Internacionales de Auditoría Financiera y Módulos de Código
**Proyecto de Maestría en Analítica de Datos | Estándar: PCAOB / AICPA / ISA 315**

---

## 📌 1. MATRIZ DE MATRICIAL DE AFIRMACIONES DE AUDITORÍA

El sistema mapea explícitamente cada afirmación contable internacional hacia una característica técnica y módulo de código del software:

| Afirmación de Auditoría | Estándar Internacional | Riesgo de Auditoría Atacado | Característica / Módulo en el Sistema |
| :--- | :--- | :--- | :--- |
| **Existencia y Ocurrencia** | ISA 315 / SOX 404 | Asientos ficticios no respaldados creados por usuarios sin autorización. | Detector de Violaciones SoD Maker-Checker (`USUARIO_REGISTRADOR == USUARIO_APROBADOR`) e Identificación de Asientos Manuales. |
| **Integridad (Completeness)** | ISA 315 / AICPA | Omisión de partidas de débito o crédito que descuadran el balance contable. | Validaciones de integridad matemática `SUM(CARGO) == SUM(ABONO)` y reconciliación vs `TOTAL_CARGOS_CABECERA`. |
| **Corte (Cut-off)** | ISA 315 / SOX 404 | Registro de transacciones en periodos contables incorrectos o posteos fuera de fecha. | AST Engine de Fechas (`DATEDIFF`), banderas de fin de semana (`DAYOFWEEK IN (0,6)`) y serie de tiempo Z-Score temporal. |
| **Exactitud y Valoración** | ISA 315 / AICPA | Manipulación deliberada de importes numéricos o errores en tasas de cambio. | Test de Ley de Benford (MAD), Distancia Multivariada de Mahalanobis ($D^2$) y comparativa paramétrica vs no paramétrica (Tukey IQR). |
| **Clasificación y Presentación** | ISA 315 / AICPA | Uso incorrecto de la estructura de cuentas de mayor o categorías erróneas. | Estandarización a 33 campos canónicos en español y Amount Splitter (+/- ➔ Cargo/Abono). |
| **Custodia y Derechos** | PCAOB / Evidence | Alteración maliciosa a posteriori de los archivos de soporte de la auditoría. | Cadena de custodia criptográfica con firma Hash SHA-256 e inmutabilidad Parquet. |
