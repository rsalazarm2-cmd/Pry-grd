# 📖 DICCIONARIO DE DATOS TÉCNICO: CAPA BRONCE Y CAPA PLATA
### Especificación de Estructura de Tablas, Tipos de Datos, Nulabilidad y Mapeo ERP (Oracle / SAP / Dynamics)
**Proyecto de Maestría en Analítica de Datos | Stack: DuckDB, Apache Parquet, Pydantic V2**

---

## 📌 1. INTRODUCCIÓN Y CONTEXTO DE ARQUITECTURA

El presente diccionario de datos define la estructura de almacenamiento de las **Capas Bronce y Plata** en la arquitectura Medallion del sistema de auditoría forense contable.

- **Capa Bronce (`bronze.parquet`):** Contiene los extractos contables crudos tal como son exportados desde los sistemas ERP de origen (sin alterar valores, preservando la firma hash SHA-256).
- **Capa Plata (`silver.parquet`):** Contiene la data estandarizada y purificada alineada a la **Taxonomía Canónica de 33 Campos en Español**, con imputación de nulos, desambiguación de tipos y cálculo de expresiones AST (deltas de fecha y separación de montos).

---

## 🥉 2. DICCIONARIO DE DATOS: CAPA BRONCE (DATA LAKE CRUDO)

### 📐 Naturaleza de la Capa Bronce:
- **Almacenamiento Físico:** `data/projects/{project_id}/bronze/bronze.parquet`
- **Firma de Custodia:** Hash SHA-256 calculado en la ingesta.
- **Tipado:** Tipos de datos inferidos directamente del CSV o Parquet original.

### 📋 Campos Típicos de Extractos Contables Crudos (Oracle EBS / SAP S/4HANA):

| Campo Crudo Típico | Tipo Parquet Inferido | Nulable | Ejemplo de Valor | Descripción del Campo Crudo |
| :--- | :--- | :-: | :--- | :--- |
| `JE_HEADER_ID` / `BELNR` | BIGINT / VARCHAR | No | `10045982` / `0100458921` | Folio o identificador del comprobante contable en el ERP. |
| `JE_CATEGORY` / `BLART` | VARCHAR | No | `Sales Journal` / `SA` | Categoría o tipo de comprobante. |
| `JE_SOURCE` / `USNAM` | VARCHAR | No | `Manual` / `Spreadsheet` | Origen o fuente del registro. |
| `CREATED_BY` / `CPUDT` | VARCHAR | No | `JDOEZ_AUD` | Usuario que creó físicamente el registro. |
| `POSTED_BY` / `PPNAME` | VARCHAR | Sí | `ABROOKS_MGR` | Usuario que autorizó/posteó el asiento. |
| `ENTERED_DR` / `WRBTR_DR` | DOUBLE / DECIMAL | No | `1500000.00` | Débito en moneda de transacción. |
| `ENTERED_CR` / `WRBTR_CR` | DOUBLE / DECIMAL | No | `0.00` | Crédito en moneda de transacción. |
| `ACCOUNTED_DR` / `DSHER` | DOUBLE / DECIMAL | No | `1500000.00` | Débito en moneda funcional (local). |
| `ACCOUNTED_CR` / `HSHER` | DOUBLE / DECIMAL | No | `0.00` | Crédito en moneda funcional (local). |
| `CURRENCY_CODE` / `WAERS` | VARCHAR | No | `COP` / `USD` | Moneda de la transacción. |
| `USER_CONVERSION_RATE` | DOUBLE | Sí | `4150.50` | Tasa de cambio aplicada. |
| `DEFAULT_EFFECTIVE_DATE` | TIMESTAMP / DATE | No | `2026-08-31 00:00:00` | Fecha contable efectiva (GL Effective Date). |
| `CREATION_DATE` | TIMESTAMP | No | `2026-08-31 23:45:12` | Timestamp exacto de creación en el sistema. |
| `CODE_COMBINATION` | VARCHAR | No | `01-1105-01-0000` | Estructura combinada de cuenta de mayor. |
| `DESCRIPTION` / `BKTXT` | VARCHAR | Sí | `Ajuste manual de cierre` | Glosa o narrativa descriptiva del comprobante. |

---

## 🥈 3. DICCIONARIO DE DATOS: CAPA PLATA (CANÓNICA DE 33 CAMPOS)

### 📐 Naturaleza de la Capa Plata:
- **Almacenamiento Físico:** `data/projects/{project_id}/silver/silver.parquet`
- **Memoria Inmutable:** `data/projects/{project_id}/.column_mapping_rules.json` (Memoria de 1 ms).
- **Tipado:** Tipado estricto definido en DuckDB y DTOs de Pydantic V2.

### 📋 Especificación de los 33 Campos Canónicos en Español:

| # | Campo Canónico Plata | Tipo SQL DuckDB | Nulable | Equivalente Oracle EBS | Equivalente SAP S/4HANA | Equivalente MS Dynamics | Regla de Transformación / Imputación Plata |
| :-: | :--- | :--- | :-: | :--- | :--- | :--- | :--- |
| **1** | `FOLIO_ASIENTO` | BIGINT | No | `JE_HEADER_ID` | `BELNR` | `Voucher` | Conversión explícita a `BIGINT`. No permite nulos. |
| **2** | `CATEGORIA_ASIENTO` | VARCHAR | No | `JE_CATEGORY` | `BLART` | `JournalType` | Trim de espacios y conversión a Mayúsculas. |
| **3** | `ORIGEN_ASIENTO` | VARCHAR | No | `JE_SOURCE` | `GL_SOURCE` | `Source` | Identifica si es `MANUAL`, `SPREADSHEET` o `SYSTEM`. |
| **4** | `USUARIO_REGISTRADOR` | VARCHAR | No | `CREATED_BY` | `USNAM` | `CreatedBy` | Usuario creador. Base para validación SoD Maker-Checker. |
| **5** | `USUARIO_APROBADOR` | VARCHAR | Sí | `POSTED_BY` | `PPNAME` | `ApprovedBy` | Usuario aprobador. Si es nulo, imputa `'NO_APROBADO'`. |
| **6** | `CARGO_MONEDA_ORIGINAL`| DECIMAL(18,2)| No | `ENTERED_DR` | `WRBTR_DR` | `AmountCurDebit` | Imputación `0.00` si es nulo. Debe ser $\ge 0.00$. |
| **7** | `ABONO_MONEDA_ORIGINAL`| DECIMAL(18,2)| No | `ENTERED_CR` | `WRBTR_CR` | `AmountCurCredit` | Imputación `0.00` si es nulo. Debe ser $\ge 0.00$. |
| **8** | `CARGO_MONEDA_FUNCIONAL`| DECIMAL(18,2)| No | `ACCOUNTED_DR` | `DSHER` | `AmountMSTDebit` | Imputación `0.00`. Campo principal de auditoría ($). |
| **9** | `ABONO_MONEDA_FUNCIONAL`| DECIMAL(18,2)| No | `ACCOUNTED_CR` | `HSHER` | `AmountMSTCredit` | Imputación `0.00`. Campo principal de auditoría ($). |
| **10** | `MONEDA` | VARCHAR | No | `CURRENCY_CODE` | `WAERS` | `CurrencyCode` | Código de moneda de 3 caracteres (ISO 4217). |
| **11** | `TASA_CAMBIO` | DECIMAL(12,6)| No | `USER_CONVERSION_RATE`| `KURSF` | `ExchRate` | Imputación `1.000000` si la moneda es local. |
| **12** | `FECHA_TASA_CAMBIO` | TIMESTAMP | Sí | `CURRENCY_CONVERSION_DATE`| `WWERT` | `ExchRateDate` | Timestamp de vigencia de la tasa de cambio. |
| **13** | `CUENTA_CONTABLE` | VARCHAR | No | `CODE_COMBINATION` | `HKONT` | `MainAccount` | Cuenta contable combinada o de mayor. |
| **14** | `PERIODO_CONTABLE` | VARCHAR | No | `PERIOD_NAME` | `MONAT` | `Period` | Nombre del periodo fiscal contable (ej. `AGO-26`). |
| **15** | `FECHA_CONTABILIZACION`| TIMESTAMP | No | `DEFAULT_EFFECTIVE_DATE`| `BUDAT` | `TransDate` | Fecha contable efectiva (GL Effective Date). |
| **16** | `FECHA_REGISTRO_CONTABLE`| TIMESTAMP| No | `CREATION_DATE` | `CPUDT + CPUTM` | `CreatedDateTime` | Timestamp físico de registro en el sistema. |
| **17** | `TOTAL_CARGOS_CABECERA`| DECIMAL(18,2)| No | `RUNNING_TOTAL_DR` | `SUM_DSHER` | `TotalDebit` | Total cargos informados en la cabecera del comprobante. |
| **18** | `TOTAL_ABONOS_CABECERA`| DECIMAL(18,2)| No | `RUNNING_TOTAL_CR` | `SUM_HSHER` | `TotalCredit` | Total abonos informados en la cabecera del comprobante. |
| **19** | `GLOSA_ASIENTO` | VARCHAR | Sí | `DESCRIPTION` | `BKTXT` | `Description` | Glosa descriptiva. Evaluada con Entropía de Shannon. |
| **20** | `NOMBRE_LIBRO_MAYOR` | VARCHAR | No | `LEDGER_NAME` | `RLDNR` | `Ledger` | Nombre del libro mayor (Primary Ledger / IFRS). |
| **21** | `MONEDA_LIBRO` | VARCHAR | No | `LEDGER_CURRENCY` | `HWAER` | `LedgerCurrency` | Moneda funcional del libro mayor (ej. `COP`). |
| **22** | `COMPANIA` | VARCHAR | No | `SEGMENT1` | `BUKRS` | `Company` | Código de sociedad o entidad legal. |
| **23** | `CENTRO_COSTO` | VARCHAR | Sí | `SEGMENT3` | `KOSTL` | `CostCenter` | Segmento de centro de costo o unidad organizativa. |
| **24** | `PROYECTO` | VARCHAR | Sí | `SEGMENT5` | `PRCTR` | `Project` | Código de proyecto o segmento auxiliar. |
| **25** | `LINEA_ASIENTO` | BIGINT | No | `JE_LINE_NUM` | `BUZEI` | `LineNum` | Número de secuencia de la línea dentro del comprobante. |
| **26** | `REFERENCIA_LINEA` | VARCHAR | Sí | `LINE_REFERENCE` | `SGTXT` | `LineTxt` | Referencia particular de la línea del asiento. |
| **27** | `ESTADO_APROBACION` | VARCHAR | No | `APPROVAL_STATUS_CODE`| `BSTAT` | `DocumentStatus` | Estado del registro (`POSTED`, `UNPOSTED`). |
| **28** | `TIPO_ASIENTO` | VARCHAR | No | `ACTUAL_FLAG` | `VART` | `PostingType` | Balance real (`A` = Actual, `B` = Budget). |
| **29** | `ID_DOCUMENTO` | BIGINT | Sí | `DOC_SEQUENCE_VALUE` | `XBLNR` | `DocumentNum` | Número de documento soporte o factura. |
| **30** | `TIPO_TASA_CAMBIO` | VARCHAR | Sí | `USER_CONVERSION_TYPE`| `KURST` | `ExchRateType` | Tipo de tasa (`Corporate`, `Spot`, `User`). |
| **31** | `SALDO_INICIAL` | DECIMAL(18,2)| Sí | `BEGINNING_BALANCE` | `SALDO_INI` | `OpeningBalance` | Saldo inicial de la cuenta contable en la fecha. |
| **32** | `SALDO_FINAL` | DECIMAL(18,2)| Sí | `ENDING_BALANCE` | `SALDO_FIN` | `ClosingBalance` | Saldo final acumulado de la cuenta contable. |
| **33** | `INDICADOR_REVERSION` | VARCHAR | Sí | `REVERSAL_STATUS` | `STJAH` | `Reversed` | Indicador si el comprobante fue reversado (`S`/`N`). |

---

## ⚡ 4. CAMPOS AST CALCULADOS DINÁMICAMENTE EN PLATA

Además de los 33 campos canónicos, el motor de la Capa Plata calcula dinámicamente cuatro columnas de auditoría derivadas:

1. **`DIFERENCIA_SEGUNDOS_APROBACION` (BIGINT):**  
   `DATEDIFF('second', FECHA_REGISTRO_CONTABLE, FECHA_CONTABILIZACION)`. Mide el tiempo transcurrido entre la creación y la contabilización.
2. **`DIA_SEMANA_CONTABLE` (VARCHAR):**  
   `STRFTIME(FECHA_CONTABILIZACION, '%A')`. Día de la semana en español ('LUNES', 'SÁBADO', 'DOMINGO').
3. **`ES_FIN_DE_SEMANA` (BOOLEAN):**  
   `TRUE` si el día es sábado o domingo; `FALSE` de lo contrario.
4. **`DESCUADRE_CABECERA_LINEAS` (DECIMAL(18,2)):**  
   `ABS(TOTAL_CARGOS_CABECERA - TOTAL_ABONOS_CABECERA)`. Mide diferencias entre débitos y créditos en la cabecera del asiento.
