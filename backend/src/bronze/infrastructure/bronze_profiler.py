from pathlib import Path
import re
import duckdb
from src.shared.domain.journal_entry import (
    ColumnProfileDTO,
    TopFrequencyItem,
)
from src.ai_translator.infrastructure.nlp_semantic_translator import NLPSemanticTranslator

def safe_path(path: Path) -> str:
    return str(path.resolve()).replace("'", "''")

_nlp_translator_instance = None
def get_nlp_classifier() -> NLPSemanticTranslator:
    global _nlp_translator_instance
    if _nlp_translator_instance is None:
        _nlp_translator_instance = NLPSemanticTranslator()
    return _nlp_translator_instance

def infer_data_type(col_name: str, raw_data_type: str, sample_values: list[str]) -> str:
    """Inferencia dinámica de tipos de datos basada 100% en inspección física de muestras."""
    if raw_data_type and raw_data_type.upper() not in ("VARCHAR", "STRING", "TEXT"):
        return raw_data_type

    valid = [s.strip() for s in sample_values if s and s.strip()]
    if not valid:
        return "VARCHAR"

    # Detección de Timestamps
    is_ts = all(re.search(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}', s) or re.search(r'\d{1,2}[/\.-]\d{1,2}[/\.-]\d{2,4}\s+\d{1,2}:\d{2}', s) for s in valid)
    if is_ts:
        return "TIMESTAMP"

    # Detección de Fechas
    is_dt = all(re.match(r'^\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}$', s) or re.match(r'^\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}$', s) or re.match(r'^\d{1,2}-[A-Za-z]{3}-\d{2,4}$', s) for s in valid)
    if is_dt:
        return "DATE"

    # Detección de Numéricos (Flotantes / Enteros / BigInt)
    clean_nums = [s.replace(",", "") for s in valid]
    if all(re.match(r'^-?\d+(\.\d+)?$', s) for s in clean_nums):
        if any("." in s for s in clean_nums):
            return "DOUBLE"
        return "BIGINT" if any(len(s) > 9 for s in valid) else "INTEGER"

    return "VARCHAR"

def profile_column(conn: duckdb.DuckDBPyConnection, target_path: Path, col_name: str, raw_data_type: str, total_rows: int) -> ColumnProfileDTO:
    classifier = get_nlp_classifier()
    domain_cat = classifier.classify_domain(col_name)
    safe_col = f'"{col_name}"'
    safe_target = safe_path(target_path)

    metrics = conn.execute(f"""
        SELECT
            SUM(CASE WHEN {safe_col} IS NULL OR trim(CAST({safe_col} AS VARCHAR)) = '' THEN 1 ELSE 0 END),
            COUNT(DISTINCT {safe_col}),
            SUM(CASE WHEN CAST({safe_col} AS VARCHAR) LIKE '%.%' THEN 1 ELSE 0 END),
            SUM(CASE WHEN CAST({safe_col} AS VARCHAR) LIKE '%,%' THEN 1 ELSE 0 END),
            MAX(length(CAST({safe_col} AS VARCHAR)))
        FROM read_parquet('{safe_target}')
    """).fetchone()

    null_count, unique_count = int(metrics[0] or 0), int(metrics[1] or 0)
    contains_dots, contains_commas = int(metrics[2] or 0) > 0, int(metrics[3] or 0) > 0
    max_len = metrics[4]
    null_pct = round((null_count / total_rows * 100) if total_rows > 0 else 0.0, 2)
    unique_ratio = round((unique_count / total_rows) if total_rows > 0 else 0.0, 4)

    freq_rows = conn.execute(f"""
        SELECT CAST({safe_col} AS VARCHAR) AS val, COUNT(*) AS f
        FROM read_parquet('{safe_target}')
        WHERE {safe_col} IS NOT NULL AND trim(CAST({safe_col} AS VARCHAR)) != ''
        GROUP BY {safe_col} ORDER BY f DESC LIMIT 5
    """).fetchall()

    top_freqs = [TopFrequencyItem(value=r[0] if r[0] is not None else "NULL", count=r[1], percentage=round((r[1] / total_rows * 100) if total_rows > 0 else 0.0, 2)) for r in freq_rows]
    sample_vals = [str(r[0]) for r in freq_rows if r[0] is not None and str(r[0]).strip() != ""]
    inferred_type = infer_data_type(col_name, raw_data_type, sample_vals)

    mean_val, min_val, max_val, sum_val = None, None, None, None
    if inferred_type in ("DOUBLE", "BIGINT", "INTEGER", "FLOAT", "DECIMAL", "NUMERIC"):
        num_stats = conn.execute(f"""
            SELECT
                AVG(TRY_CAST(replace(CAST({safe_col} AS VARCHAR), ',', '') AS DOUBLE)),
                MIN(TRY_CAST(replace(CAST({safe_col} AS VARCHAR), ',', '') AS DOUBLE)),
                MAX(TRY_CAST(replace(CAST({safe_col} AS VARCHAR), ',', '') AS DOUBLE)),
                SUM(TRY_CAST(replace(CAST({safe_col} AS VARCHAR), ',', '') AS DOUBLE))
            FROM read_parquet('{safe_target}')
        """).fetchone()
        if num_stats[0] is not None:
            mean_val = round(float(num_stats[0]), 2)
            min_val = str(round(float(num_stats[1]), 2)) if num_stats[1] is not None else None
            max_val = str(round(float(num_stats[2]), 2)) if num_stats[2] is not None else None
            sum_val = round(float(num_stats[3]), 2) if num_stats[3] is not None else None

    return ColumnProfileDTO(
        column_name=col_name, domain_category=domain_cat, data_type=inferred_type, null_count=null_count,
        total_rows=total_rows, null_percentage=null_pct, unique_count=unique_count, uniqueness_ratio=unique_ratio,
        min_value=min_val, max_value=max_val, mean_value=mean_val, sum_value=sum_val,
        max_length=int(max_len) if max_len is not None else None, top_frequencies=top_freqs, sample_values=sample_vals,
        contains_dots=contains_dots, contains_commas=contains_commas
    )
