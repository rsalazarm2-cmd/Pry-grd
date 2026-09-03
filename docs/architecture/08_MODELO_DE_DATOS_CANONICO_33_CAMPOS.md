# 📋 08. MODELO DE DATOS CANÓNICO Y TAXONOMÍA DE 33 CAMPOS
### Estándar de Dominio para Oracle EBS, SAP S/4HANA y MS Dynamics 365
**Proyecto de Maestría en Analítica de Datos | Lenguaje: Español Estricto Contable**

---

## 📌 1. ESPECIFICACIÓN COMPLETA DEL MODELO CANÓNICO DE AUDITORÍA

La Capa Plata estandariza los extractos de cualquier ERP a la taxonomía canónica de 33 campos en español:

| # | Campo Canónico | Tipo de Dato | Nulable | Equivalente Oracle EBS | Equivalente SAP S/4HANA | Equivalente MS Dynamics | Descripción de Negocio Contable |
| :-: | :--- | :--- | :-: | :--- | :--- | :--- | :--- |
| **1** | `FOLIO_ASIENTO` | BIGINT | No | `JE_HEADER_ID` | `BELNR` | `Voucher` | Identificador único del encabezado del comprobante |
| **2** | `CATEGORIA_ASIENTO` | VARCHAR | No | `JE_CATEGORY` | `BLART` | `JournalType` | Categoría del comprobante contable |
| **3** | `ORIGEN_ASIENTO` | VARCHAR | No | `JE_SOURCE` | `USNAM / GL_SOURCE` | `Source` | Origen (SPREADSHEET, MANUAL, SYSTEM, INTERFACE) |
| **4** | `USUARIO_REGISTRADOR` | VARCHAR | No | `CREATED_BY` | `USNAM` | `CreatedBy` | Usuario que creó el asiento en el sistema |
| **5** | `USUARIO_APROBADOR` | VARCHAR | Sí | `POSTED_BY` | `PPNAME` | `ApprovedBy` | Usuario que autorizó/posteó el asiento |
| **6** | `CARGO_MONEDA_ORIGINAL`| DECIMAL(18,2)| No | `ENTERED_DR` | `WRBTR_DR` | `AmountCurDebit` | Importe de débito en moneda de transacción |
| **7** | `ABONO_MONEDA_ORIGINAL`| DECIMAL(18,2)| No | `ENTERED_CR` | `WRBTR_CR` | `AmountCurCredit` | Importe de crédito en moneda de transacción |
| **8** | `CARGO_MONEDA_FUNCIONAL`| DECIMAL(18,2)| No | `ACCOUNTED_DR` | `DSHER` | `AmountMSTDebit` | Importe de débito en moneda funcional |
| **9** | `ABONO_MONEDA_FUNCIONAL`| DECIMAL(18,2)| No | `ACCOUNTED_CR` | `HSHER` | `AmountMSTCredit` | Importe de crédito en moneda funcional |
| **10** | `MONEDA` | VARCHAR | No | `CURRENCY_CODE` | `WAERS` | `CurrencyCode` | Código de moneda de la transacción (COP, USD, EUR) |
| **11** | `TASA_CAMBIO` | DECIMAL(12,6)| No | `USER_CONVERSION_RATE`| `KURSF` | `ExchRate` | Tasa de cambio aplicada al comprobante |
| **12** | `FECHA_TASA_CAMBIO` | TIMESTAMP | Sí | `CURRENCY_CONVERSION_DATE`| `WWERT` | `ExchRateDate` | Fecha efectiva de la tasa de cambio |
| **13** | `CUENTA_CONTABLE` | VARCHAR | No | `CODE_COMBINATION` | `HKONT` | `MainAccount` | Código de combinación contable de mayor |
| **14** | `PERIODO_CONTABLE` | VARCHAR | No | `PERIOD_NAME` | `MONAT` | `Period` | Nombre del periodo fiscal contable |
| **15** | `FECHA_CONTABILIZACION`| TIMESTAMP | No | `DEFAULT_EFFECTIVE_DATE`| `BUDAT` | `TransDate` | Fecha contable efectiva GL Date |
| **16** | `FECHA_REGISTRO_CONTABLE`| TIMESTAMP| No | `CREATION_DATE` | `CPUDT + CPUTM` | `CreatedDateTime` | Timestamp de creación física en el sistema |
| **17** | `TOTAL_CARGOS_CABECERA`| DECIMAL(18,2)| No | `RUNNING_TOTAL_DR` | `SUM_DSHER` | `TotalDebit` | Total cargos informados en la cabecera |
| **18** | `TOTAL_ABONOS_CABECERA`| DECIMAL(18,2)| No | `RUNNING_TOTAL_CR` | `SUM_HSHER` | `TotalCredit` | Total abonos informados en la cabecera |
| **19** | `GLOSA_ASIENTO` | VARCHAR | Sí | `DESCRIPTION` | `BKTXT` | `Description` | Glosa o descripción narrativa |
| **20** | `NOMBRE_LIBRO_MAYOR` | VARCHAR | No | `LEDGER_NAME` | `RLDNR` | `Ledger` | Nombre del libro mayor (Primary/Secondary Ledger) |
| **21** | `MONEDA_LIBRO` | VARCHAR | No | `LEDGER_CURRENCY` | `HWAER` | `LedgerCurrency` | Moneda funcional del libro mayor |
| **22** | `COMPANIA` | VARCHAR | No | `SEGMENT1` | `BUKRS` | `Company` | Segmento de entidad legal o sociedad |
| **23** | `CENTRO_COSTO` | VARCHAR | Sí | `SEGMENT3` | `KOSTL` | `CostCenter` | Segmento de centro de costos |
| **24** | `PROYECTO` | VARCHAR | Sí | `SEGMENT5` | `PRCTR` | `Project` | Segmento de proyecto |
| **25** | `LINEA_ASIENTO` | BIGINT | No | `JE_LINE_NUM` | `BUZEI` | `LineNum` | Secuencia numérica de la línea dentro del asiento |
| **26** | `REFERENCIA_LINEA` | VARCHAR | Sí | `LINE_REFERENCE` | `SGTXT` | `LineTxt` | Referencia descriptiva de la línea |
| **27** | `ESTADO_APROBACION` | VARCHAR | No | `APPROVAL_STATUS_CODE`| `BSTAT` | `DocumentStatus` | Estado del comprobante (POSTED, UNPOSTED) |
| **28** | `TIPO_ASIENTO` | VARCHAR | No | `ACTUAL_FLAG` | `VART` | `PostingType` | Tipo de balance (ACTUAL, BUDGET, ENCUMBRANCE) |
| **29** | `ID_DOCUMENTO` | BIGINT | Sí | `DOC_SEQUENCE_VALUE` | `XBLNR` | `DocumentNum` | Número de documento físico o factura |
| **30** | `TIPO_TASA_CAMBIO` | VARCHAR | Sí | `USER_CONVERSION_TYPE`| `KURST` | `ExchRateType` | Tipo de tasa de cambio (Corporate, Spot, User) |
| **31** | `SALDO_INICIAL` | DECIMAL(18,2)| Sí | `BEGINNING_BALANCE` | `SALDO_INI` | `OpeningBalance` | Saldo inicial de la cuenta contable |
| **32** | `SALDO_FINAL` | DECIMAL(18,2)| Sí | `ENDING_BALANCE` | `SALDO_FIN` | `ClosingBalance` | Saldo final de la cuenta contable |
| **33** | `INDICADOR_REVERSION` | VARCHAR | Sí | `REVERSAL_STATUS` | `STJAH / STBLG` | `Reversed` | Indicador si el asiento fue reversado |
