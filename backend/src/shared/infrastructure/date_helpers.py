"""
Módulo helper de infraestructura para la construcción de expresiones SQL
de parseo inteligente de fechas y timestamps en DuckDB.

Garantiza la inferencia correcta de fechas con años de 2 o 4 dígitos 
(ej. '29/05/26' -> 2026-05-29, '01/05/26' -> 2026-05-01, '2026-05-29')
tanto al inicio como al final de la cadena de texto.
"""

def build_smart_date_cast_sql(col_expr: str) -> str:
    """
    Construye una sentencia CASE en SQL DuckDB para convertir una expresión
    de texto en DATE de forma inteligente detectando el formato del año.

    Args:
        col_expr: Expresión SQL de la columna o valor a castear.

    Returns:
        String de sentencia CASE en SQL DuckDB.
    """
    s = f"CAST({col_expr} AS VARCHAR)"
    return (
        f"CASE "
        f"WHEN {col_expr} IS NULL OR trim({s}) = '' THEN NULL "
        f"WHEN regexp_matches(trim({s}), '^[0-9]{{4}}[-/][0-9]{{1,2}}[-/][0-9]{{1,2}}') THEN "
        f"TRY_CAST(trim({s}) AS DATE) "
        f"WHEN regexp_matches(trim({s}), '^[0-9]{{1,2}}[-/][0-9]{{1,2}}[-/][0-9]{{4}}') THEN "
        f"COALESCE("
        f"TRY_STRPTIME(replace(split_part(trim({s}), ' ', 1), '-', '/'), '%d/%m/%Y'), "
        f"TRY_STRPTIME(replace(split_part(trim({s}), ' ', 1), '-', '/'), '%m/%d/%Y'), "
        f"TRY_CAST(trim({s}) AS DATE)"
        f") "
        f"WHEN regexp_matches(trim({s}), '^[0-9]{{1,2}}[-/][0-9]{{1,2}}[-/][0-9]{{2}}') THEN "
        f"COALESCE("
        f"TRY_STRPTIME(replace(split_part(trim({s}), ' ', 1), '-', '/'), '%d/%m/%y'), "
        f"TRY_STRPTIME(replace(split_part(trim({s}), ' ', 1), '-', '/'), '%m/%d/%y'), "
        f"TRY_CAST(trim({s}) AS DATE)"
        f") "
        f"ELSE TRY_CAST(trim({s}) AS DATE) "
        f"END"
    )

def build_smart_timestamp_cast_sql(col_expr: str) -> str:
    """
    Construye una sentencia CASE en SQL DuckDB para convertir una expresión
    de texto en TIMESTAMP de forma inteligente detectando la hora y fecha.

    Args:
        col_expr: Expresión SQL de la columna o valor a castear.

    Returns:
        String de sentencia CASE en SQL DuckDB.
    """
    s = f"CAST({col_expr} AS VARCHAR)"
    return (
        f"CASE "
        f"WHEN {col_expr} IS NULL OR trim({s}) = '' THEN NULL "
        f"WHEN regexp_matches(trim({s}), '^[0-9]{{4}}[-/][0-9]{{1,2}}[-/][0-9]{{1,2}}') THEN "
        f"TRY_CAST(trim({s}) AS TIMESTAMP) "
        f"WHEN regexp_matches(trim({s}), '^[0-9]{{1,2}}[-/][0-9]{{1,2}}[-/][0-9]{{4}}') THEN "
        f"COALESCE("
        f"TRY_STRPTIME(replace(trim({s}), '-', '/'), '%d/%m/%Y %H:%M:%S'), "
        f"TRY_STRPTIME(replace(trim({s}), '-', '/'), '%d/%m/%Y %H:%M'), "
        f"TRY_STRPTIME(replace(trim({s}), '-', '/'), '%d/%m/%Y'), "
        f"TRY_STRPTIME(replace(trim({s}), '-', '/'), '%m/%d/%Y %H:%M:%S'), "
        f"TRY_STRPTIME(replace(trim({s}), '-', '/'), '%m/%d/%Y'), "
        f"TRY_CAST(trim({s}) AS TIMESTAMP)"
        f") "
        f"WHEN regexp_matches(trim({s}), '^[0-9]{{1,2}}[-/][0-9]{{1,2}}[-/][0-9]{{2}}') THEN "
        f"COALESCE("
        f"TRY_STRPTIME(replace(trim({s}), '-', '/'), '%d/%m/%y %H:%M:%S'), "
        f"TRY_STRPTIME(replace(trim({s}), '-', '/'), '%d/%m/%y %H:%M'), "
        f"TRY_STRPTIME(replace(trim({s}), '-', '/'), '%d/%m/%y'), "
        f"TRY_STRPTIME(replace(trim({s}), '-', '/'), '%m/%d/%y %H:%M:%S'), "
        f"TRY_STRPTIME(replace(trim({s}), '-', '/'), '%m/%d/%y'), "
        f"TRY_CAST(trim({s}) AS TIMESTAMP)"
        f") "
        f"ELSE TRY_CAST(trim({s}) AS TIMESTAMP) "
        f"END"
    )
