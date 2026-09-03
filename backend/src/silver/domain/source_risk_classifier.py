"""Clasificador de Riesgo del Origen de Asientos Contables.

Clasifica asientos como MANUAL (Alto Riesgo), AUTOMATICO (Bajo Riesgo), o MIXTO (Medio).
Funciona de forma agnóstica para Oracle EBS, SAP, NetSuite y Dynamics 365.
"""
from typing import Dict

MANUAL_SOURCES = {
    "MANUAL", "SPREADSHEET", "EXCEL", "JOURNAL", "SA", "AX IMPORT",
    "DATA ENTITY", "USER ENTRY", "ADJUSTMENT", "AJUSTE", "MANUAL ENTRY",
    "PLANILLA", "RECLASIFICACION", "PROVISION", "205", "604", "0", "145"
}

AUTOMATIC_SOURCES = {
    "PAYABLES", "RECEIVABLES", "ASSETS", "INVENTORY", "PAYROLL", "PURCHASING",
    "AP", "AR", "FA", "MM", "HR", "PO", "SO", "RE", "RV", "AA", "BILLING",
    "FACTURACION", "TESORERIA", "TREASURY", "134"
}

MIXED_SOURCES = {
    "CONSOLIDATION", "REVALUATION", "ALLOCATION", "INTERCOMPANY", "RESERVE",
    "CIERRE", "REVALUACION", "ASIGNACION"
}


def classify_source_risk(origin_value: str) -> str:
    """Clasifica una cadena de origen en 'MANUAL', 'AUTOMATICO' o 'MIXTO'."""
    val = (origin_value or "").upper().strip()

    if any(pattern in val for pattern in MANUAL_SOURCES):
        return "MANUAL"
    if any(pattern in val for pattern in AUTOMATIC_SOURCES):
        return "AUTOMATICO"
    if any(pattern in val for pattern in MIXED_SOURCES):
        return "MIXTO"
    return "MANUAL" if val.isdigit() else "DESCONOCIDO"


def get_risk_level(classification: str) -> str:
    """Devuelve el nivel de riesgo en auditoría para cada clasificación."""
    cls = (classification or "").upper().strip()
    if cls == "MANUAL":
        return "ALTO"
    if cls == "AUTOMATICO":
        return "BAJO"
    return "MEDIO"


def build_duckdb_source_risk_expression(origen_col_name: str = "ORIGEN_ASIENTO") -> str:
    """Genera la expresión SQL nativa de DuckDB para calcular TIPO_RIESGO_ORIGEN."""
    col = f'"{origen_col_name}"'
    base = f"UPPER(TRIM(CAST({col} AS VARCHAR)))"

    manual_conds = " OR ".join([f"{base} LIKE '%{src}%'" for src in MANUAL_SOURCES])
    auto_conds = " OR ".join([f"{base} LIKE '%{src}%'" for src in AUTOMATIC_SOURCES])
    mixed_conds = " OR ".join([f"{base} LIKE '%{src}%'" for src in MIXED_SOURCES])

    return f"""
    CASE
        WHEN {manual_conds} THEN 'MANUAL'
        WHEN {auto_conds} THEN 'AUTOMATICO'
        WHEN {mixed_conds} THEN 'MIXTO'
        WHEN regexp_matches({base}, '^[0-9]+$') THEN 'MANUAL'
        ELSE 'DESCONOCIDO'
    END
    """
