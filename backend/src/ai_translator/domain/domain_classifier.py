"""Clasificador de Dominio y Motor de Expansión de Abreviaturas ERP.

Agnóstico de plataforma: funciona con Oracle EBS, SAP, NetSuite, Dynamics, etc.
El NLP L2 (embeddings semánticos) es el motor principal.
El L1 (diccionario) solo acelera las columnas más comunes.
"""
from typing import Dict, List

BUSINESS_DOMAINS: Dict[str, str] = {
    "1. Identificadores y Control ERP": "System IDs, sequence numbers, batch names, status codes, header identifiers, posting flags, document IDs",
    "2. Estructura Contable y Libros": "Chart of accounts, code combination, ledger name, ledger currency, journal source, journal category",
    "3. Métricas Financieras y Moneda": "Entered debit, entered credit, accounted debit, accounted credit, currency, conversion rate, exchange rate, debits, credits, balances, amounts",
    "4. Trazabilidad de Fechas": "Accounting period, effective date, creation date, posted date, update date, GL date, fiscal period, timestamps",
    "5. Auditoría de Usuarios": "Created by, posted by, user ID, last updated by, WHO posted batch, authorizer, approver, registrant",
    "6. Narrativas y Descripciones": "Journal description, header description, line description, notes, comments, textual explanations, narratives",
}

# L1: Mapeo directo 1-a-1. Solo las columnas MÁS seguras y comunes.
# Entradas con semántica incorrecta fueron ELIMINADAS para que el NLP L2 las resuelva.
ENGLISH_TO_SPANISH_MAP: Dict[str, str] = {
    "JE_HEADER_ID": "FOLIO_ASIENTO",
    "HEADER_ID": "FOLIO_ASIENTO",
    "JE_BATCH_NAME": "LOTE_ASIENTO",
    "JE_CATEGORY": "CATEGORIA_ASIENTO",
    "JE_SOURCE": "ORIGEN_ASIENTO",
    "JE_DESCRIPTION": "GLOSA_ASIENTO",
    "ENTERED_DR": "CARGO_MONEDA_ORIGINAL",
    "ENTERED_CR": "ABONO_MONEDA_ORIGINAL",
    "ACCOUNTED_DR": "CARGO_MONEDA_FUNCIONAL",
    "ACCOUNTED_CR": "ABONO_MONEDA_FUNCIONAL",
    "CODE_COMBINATION": "CUENTA_CONTABLE",
    "CODE_COMBINATION_ID": "ID_CUENTA_CONTABLE",
    "LEDGER_NAME": "NOMBRE_LIBRO_MAYOR",
    "LEDGER_ID": "ID_LIBRO_MAYOR",
    "LEDGER_CURRENCY": "MONEDA_LIBRO",
    "ACCOUNTING_PERIOD": "PERIODO_CONTABLE",
    "ACCOUNTING_PERIOD_FOR_BATCH": "PERIODO_CONTABLE_LOTE",
    "POSTED_BY_GL": "USUARIO_APROBADOR",
    "WHO_POSTED_BATCH": "USUARIO_APROBADOR_LOTE",
    "CREATED_IN_GL": "USUARIO_REGISTRADOR",
    "DATE_HEADER_CREATED_IN_GL": "FECHA_REGISTRO_CONTABLE",
    "BATCH_CREATION_DATE_IN_GL": "FECHA_CREACION_LOTE",
    "CREATION_DATE": "FECHA_REGISTRO_CONTABLE",
    "LAST_UPDATE_DATE": "FECHA_ULTIMA_ACTUALIZACION",
    "LAST_UPDATED_BY": "USUARIO_ULTIMA_ACTUALIZACION",
    "JE_EFFECTIVE_DATE": "FECHA_CONTABILIZACION",
    "POSTED_DATE": "FECHA_CONTABILIZACION",
    "GL_DATE": "FECHA_CONTABILIZACION",
    "CURRENCY_CODE": "MONEDA",
    "DOC_SEQUENCE_VALUE": "ID_DOCUMENTO",
    "STATUS": "ESTADO_APROBACION",
    "JE_BATCH_STATUS_CODE": "ESTADO_LOTE_ASIENTO",
    "POSTING_REQUEST_ID": "ID_SOLICITUD_CONTABILIZACION",
    "CHART_OF_ACCOUNTS_ID": "ID_PLAN_CUENTAS",
    "CURRENCY_CONVERSION_RATE": "TASA_CAMBIO",
    "ACTUAL_FLAG": "INDICADOR_REVERSION",
}

ERP_TOKEN_SPANISH: Dict[str, str] = {
    "CREATION": "CREACION", "DATE": "FECHA", "POSTED": "CONTABILIZACION",
    "LAST": "ULTIMA", "UPDATE": "ACTUALIZACION", "UPDATED": "ACTUALIZADO",
    "WHO": "USUARIO", "BATCH": "LOTE", "STATUS": "ESTADO", "CODE": "CODIGO",
    "POSTING": "CONTABILIZACION", "REQUEST": "SOLICITUD", "ID": "ID",
    "CHART": "PLAN", "OF": "DE", "ACCOUNTS": "CUENTAS",
    "ACCOUNTING": "CONTABLE", "PERIOD": "PERIODO", "FOR": "PARA",
    "USER": "USUARIO", "SOURCE": "ORIGEN", "CATEGORY": "CATEGORIA",
    "NAME": "NOMBRE", "JOURNAL": "ASIENTO", "ENTRY": "ASIENTO",
    "HEADER": "CABECERA", "DESCRIPTION": "GLOSA", "CURRENCY": "MONEDA",
    "AMOUNT": "MONTO", "TOTAL": "TOTAL", "DEBIT": "CARGO", "CREDIT": "ABONO",
    "ENTERED": "ORIGINAL", "ACCOUNTED": "FUNCIONAL", "DR": "CARGO", "CR": "ABONO",
    "LEDGER": "LIBRO", "VAL": "VALOR", "SEQ": "SECUENCIA", "DOC": "DOCUMENTO"
}

def translate_raw_column_name_to_spanish(column_name: str) -> str:
    tokens = column_name.upper().strip().split("_")
    translated_tokens = [ERP_TOKEN_SPANISH.get(t, t) for t in tokens if t]
    return "_".join(translated_tokens)


SPANISH_TO_ENGLISH_MAP: Dict[str, str] = {v: k for k, v in ENGLISH_TO_SPANISH_MAP.items()}

OFFICIAL_SPANISH_SCHEMA: Dict[str, str] = {
    "FOLIO_ASIENTO": "Número o identificador de cabecera del asiento contable o póliza (Header ID, Journal Entry ID)",
    "LOTE_ASIENTO": "Nombre o identificador del lote de asientos contables (Batch Name, Batch ID)",
    "CATEGORIA_ASIENTO": "Categoría o tipo de transacción contable (Journal Category, Category Name)",
    "ORIGEN_ASIENTO": "Origen o fuente del asiento contable (Journal Source, Source System)",
    "GLOSA_ASIENTO": "Descripción o narrativa explicativa del asiento contable (Journal Description, Header Description)",
    "CARGO_MONEDA_ORIGINAL": "Monto debitado en moneda de transacción u original (Entered Debit, Transaction Debit)",
    "ABONO_MONEDA_ORIGINAL": "Monto acreditado en moneda de transacción u original (Entered Credit, Transaction Credit)",
    "CARGO_MONEDA_FUNCIONAL": "Monto debitado en moneda funcional o local (Accounted Debit, Functional Debit)",
    "ABONO_MONEDA_FUNCIONAL": "Monto acreditado en moneda funcional o local (Accounted Credit, Functional Credit)",
    "TOTAL_CARGOS_CABECERA": "Suma total de cargos o débitos registrados en la cabecera (Total Entered Dr, Header Debit Total)",
    "TOTAL_ABONOS_CABECERA": "Suma total de abonos o créditos registrados en la cabecera (Total Entered Cr, Header Credit Total)",
    "CUENTA_CONTABLE": "Combinación de código de cuenta contable o plan de cuentas (Code Combination, Account Code)",
    "NOMBRE_LIBRO_MAYOR": "Nombre del libro mayor o contabilidad principal (Ledger Name, Book Name)",
    "MONEDA_LIBRO": "Moneda funcional del libro mayor (Ledger Currency, Functional Currency)",
    "PERIODO_CONTABLE": "Período fiscal o mes contable (Accounting Period, Fiscal Period, Period Name)",
    "USUARIO_REGISTRADOR": "Usuario que creó o registró el asiento contable (Created By, Created User)",
    "USUARIO_APROBADOR": "Usuario que aprobó o contabilizó el asiento en el libro mayor (Posted By, Approved User)",
    "FECHA_REGISTRO_CONTABLE": "Fecha de creación o registro en el sistema contable (Creation Date, Entry Date)",
    "FECHA_CONTABILIZACION": "Fecha efectiva de contabilización o fecha GL (Effective Date, Posted Date, GL Date)",
    "MONEDA": "Código de moneda de la transacción (Currency Code, ISO Currency)",
    "ID_DOCUMENTO": "Número de secuencia o valor de documento fiscal (Document Sequence Value, Document ID)",
    "ESTADO_APROBACION": "Estado de aprobación o contabilización del lote/asiento (Status Code, Batch Status)",
    "TASA_CAMBIO": "Tasa de conversión o tipo de cambio de moneda (Conversion Rate, Exchange Rate)",
    "INDICADOR_REVERSION": "Indicador o bandera de reversión de asiento (Actual Flag, Reversal Indicator)",
}

OFFICIAL_ENGLISH_SCHEMA: Dict[str, str] = {
    "JE_HEADER_ID": "Journal entry header unique identifier",
    "JE_BATCH_NAME": "Journal entry batch name or group ID",
    "JE_CATEGORY": "Journal transaction category or type",
    "JE_SOURCE": "Journal entry source application or subsystem",
    "JE_DESCRIPTION": "Journal entry header description or narrative",
    "ENTERED_DR": "Entered transaction debit amount",
    "ENTERED_CR": "Entered transaction credit amount",
    "ACCOUNTED_DR": "Accounted functional debit amount",
    "ACCOUNTED_CR": "Accounted functional credit amount",
    "CODE_COMBINATION": "General ledger account code combination",
    "LEDGER_NAME": "Ledger or primary book name",
    "LEDGER_CURRENCY": "Ledger functional currency code",
    "ACCOUNTING_PERIOD": "Accounting fiscal period name",
    "CREATED_BY": "User who created the journal entry",
    "POSTED_BY": "User who approved or posted the batch to GL",
    "CREATION_DATE": "Journal entry creation timestamp",
    "POSTED_DATE": "GL posting effective date",
    "CURRENCY_CODE": "Transaction currency ISO code",
    "STATUS": "Batch or journal posting status code",
}


# Abreviaturas genéricas de contabilidad y ERP.
# Agnóstico de plataforma: expande columnas de Oracle, SAP, NetSuite, Dynamics, etc.
COMMON_ABBREVIATIONS: Dict[str, str] = {
    "GL": "General Ledger", "JE": "Journal Entry",
    "DR": "Debit", "CR": "Credit",
    "AP": "Accounts Payable", "AR": "Accounts Receivable",
    "FA": "Fixed Assets", "FX": "Foreign Exchange",
    "PO": "Purchase Order", "SO": "Sales Order",
    "ID": "Identifier", "NUM": "Number",
    "QTY": "Quantity", "AMT": "Amount",
    "DESC": "Description", "HDR": "Header",
    "DTL": "Detail", "TXN": "Transaction",
    "ACCT": "Account", "CURR": "Currency",
    "CONV": "Conversion", "UPD": "Update",
    "DOC": "Document", "SEQ": "Sequence",
    "DT": "Date", "TS": "Timestamp",
    "FLG": "Flag", "IND": "Indicator",
    "SRC": "Source", "TGT": "Target",
    "GRP": "Group", "CAT": "Category",
    "BAL": "Balance", "TOT": "Total",
    "REF": "Reference", "XREF": "Cross Reference",
    "ORG": "Organization", "CO": "Company",
    "CC": "Cost Center", "FY": "Fiscal Year",
    "YR": "Year", "MO": "Month", "QTR": "Quarter",
    "EFF": "Effective", "ACT": "Actual",
    "BUD": "Budget", "ENC": "Encumbrance",
    "REV": "Revenue", "EXP": "Expense",
    "FUNC": "Functional", "LN": "Line",
}


def expand_erp_acronyms(column_name: str) -> str:
    """Expande abreviaturas ERP a lenguaje natural para potenciar el NLP.

    Agnóstico de plataforma. Ejemplo:
        DATE_HEADER_CREATED_IN_GL → 'Date Header Created In General Ledger'
        ACCOUNTED_DR             → 'Accounted Debit'
    """
    tokens = column_name.upper().strip().split("_")
    expanded: List[str] = []
    for token in tokens:
        if token in COMMON_ABBREVIATIONS:
            expanded.append(COMMON_ABBREVIATIONS[token])
        else:
            expanded.append(token.title())
    return " ".join(expanded)
