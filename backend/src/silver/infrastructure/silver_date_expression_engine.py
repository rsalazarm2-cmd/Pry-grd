"""Motor de Expresiones Vectorizadas de Fecha sobre Parquet (DuckDB Nativo).

Implementa los cálculos de CU-01 (Redundancia %), CU-02 (DATEDIFF) y
CU-03 (STRFTIME/DAYOFWEEK) directamente en DuckDB sin cargar datos a Python.
"""

import logging
from pathlib import Path

import duckdb

from src.silver.domain.date_expression_ast import (
    DateDeltaResultDTO,
    DateRedundancyResultDTO,
    HistogramBucketDTO,
    WeekdayBucketDTO,
    WeekdayResultDTO,
)

logger = logging.getLogger(__name__)

_HISTOGRAM_LABELS = [
    ("0-60s", 0, 60),
    ("1-5min", 60, 300),
    ("5-30min", 300, 1800),
    ("30min-1h", 1800, 3600),
    ("1-24h", 3600, 86400),
    (">24h", 86400, None),
]


def _safe(path: Path) -> str:
    return str(path.resolve()).replace("'", "''")


def _validate_column(conn: duckdb.DuckDBPyConnection, pq: str, col: str) -> bool:
    schema = conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{pq}')").fetchall()
    return col.upper() in [r[0].upper() for r in schema]


class SilverDateExpressionEngine:
    """Motor DuckDB nativo para expresiones vectorizadas de fecha."""

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self._conn = conn

    def list_date_columns(self, parquet_path: str) -> list[str]:
        pq = _safe(Path(parquet_path))
        schema = self._conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{pq}')").fetchall()
        date_types = {"DATE", "TIMESTAMP", "TIMESTAMP WITH TIME ZONE"}
        return [r[0] for r in schema if r[1].upper() in date_types]

    def compute_date_redundancy(
        self, parquet_path: str, col_a: str, col_b: str
    ) -> DateRedundancyResultDTO:
        """CU-01: Calcula % de coincidencia exacta entre 2 columnas de fecha."""
        pq = _safe(Path(parquet_path))
        if not _validate_column(self._conn, pq, col_a) or not _validate_column(self._conn, pq, col_b):
            return DateRedundancyResultDTO(date_column_a=col_a, date_column_b=col_b)

        query = f"""
            SELECT COUNT(*) AS total,
                   COUNT(*) FILTER (WHERE TRY_CAST("{col_a}" AS TIMESTAMP) = TRY_CAST("{col_b}" AS TIMESTAMP)) AS matching
            FROM read_parquet('{pq}')
        """
        row = self._conn.execute(query).fetchone()
        total, matching = int(row[0]), int(row[1])
        pct = round((matching / total) * 100, 2) if total > 0 else 0.0

        return DateRedundancyResultDTO(
            date_column_a=col_a, date_column_b=col_b, total_rows=total,
            matching_rows=matching, match_percentage=pct, are_identical=(pct == 100.0),
        )

    def compute_date_delta(
        self, parquet_path: str, col_a: str, col_b: str
    ) -> DateDeltaResultDTO:
        """CU-02: Calcula estadísticas de DATEDIFF('second', col_a, col_b)."""
        pq = _safe(Path(parquet_path))
        if not _validate_column(self._conn, pq, col_a) or not _validate_column(self._conn, pq, col_b):
            return DateDeltaResultDTO(source_column_a=col_a, source_column_b=col_b)

        stats_query = f"""
            SELECT COUNT(*) AS total, COALESCE(MIN(ABS(delta)), 0) AS min_d,
                   COALESCE(MAX(ABS(delta)), 0) AS max_d, COALESCE(AVG(ABS(delta)), 0) AS avg_d,
                   COUNT(*) FILTER (WHERE ABS(delta) < 60) AS rapid
            FROM (
                SELECT DATEDIFF('second', TRY_CAST("{col_a}" AS TIMESTAMP), TRY_CAST("{col_b}" AS TIMESTAMP)) AS delta
                FROM read_parquet('{pq}') WHERE "{col_a}" IS NOT NULL AND "{col_b}" IS NOT NULL
            )
        """
        row = self._conn.execute(stats_query).fetchone()
        result = DateDeltaResultDTO(
            source_column_a=col_a, source_column_b=col_b, total_rows=int(row[0]),
            min_delta_seconds=int(row[1]), max_delta_seconds=int(row[2]),
            avg_delta_seconds=round(float(row[3]), 2), rapid_approvals_count=int(row[4]),
        )
        result.histogram_buckets = self._build_histogram(pq, col_a, col_b)
        return result

    def _build_histogram(self, pq: str, col_a: str, col_b: str) -> list[HistogramBucketDTO]:
        cases = [
            f"COUNT(*) FILTER (WHERE abs_d >= {lo} AND abs_d < {hi}) AS \"{label}\"" if hi is not None
            else f"COUNT(*) FILTER (WHERE abs_d >= {lo}) AS \"{label}\""
            for label, lo, hi in _HISTOGRAM_LABELS
        ]
        query = f"""
            SELECT {', '.join(cases)} FROM (
                SELECT ABS(DATEDIFF('second', TRY_CAST("{col_a}" AS TIMESTAMP), TRY_CAST("{col_b}" AS TIMESTAMP))) AS abs_d
                FROM read_parquet('{pq}') WHERE "{col_a}" IS NOT NULL AND "{col_b}" IS NOT NULL
            )
        """
        row = self._conn.execute(query).fetchone()
        return [HistogramBucketDTO(label=_HISTOGRAM_LABELS[i][0], count=int(row[i])) for i in range(len(_HISTOGRAM_LABELS))]

    def compute_weekday_distribution(
        self, parquet_path: str, date_column: str
    ) -> WeekdayResultDTO:
        """CU-03: Calcula distribución de día de semana + flag fin de semana."""
        pq = _safe(Path(parquet_path))
        if not _validate_column(self._conn, pq, date_column):
            return WeekdayResultDTO(source_column=date_column)

        query = f"""
            SELECT
                CASE DAYOFWEEK(TRY_CAST("{date_column}" AS TIMESTAMP))
                    WHEN 0 THEN 'DOMINGO' WHEN 1 THEN 'LUNES' WHEN 2 THEN 'MARTES'
                    WHEN 3 THEN 'MIERCOLES' WHEN 4 THEN 'JUEVES' WHEN 5 THEN 'VIERNES' WHEN 6 THEN 'SABADO'
                END AS dia,
                COUNT(*) AS cnt, DAYOFWEEK(TRY_CAST("{date_column}" AS TIMESTAMP)) AS dow
            FROM read_parquet('{pq}') WHERE "{date_column}" IS NOT NULL
            GROUP BY dia, dow ORDER BY dow
        """
        rows = self._conn.execute(query).fetchall()
        total = sum(r[1] for r in rows)
        weekend = sum(r[1] for r in rows if r[2] in (0, 6))
        pct = round((weekend / total) * 100, 2) if total > 0 else 0.0

        return WeekdayResultDTO(
            source_column=date_column, total_rows=total, weekend_count=weekend,
            weekend_percentage=pct, weekday_distribution=[WeekdayBucketDTO(day=r[0], count=int(r[1])) for r in rows],
        )
