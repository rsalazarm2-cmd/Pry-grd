"""Motor de Separación de Partida Doble: 1 columna signada → CARGO / ABONO.

Implementa CU-04: transforma una columna de montos con signo (+/-)
en dos columnas independientes (CARGO para positivos, ABONO para negativos).
Todo el cómputo se ejecuta en DuckDB sin cargar datos a Python.

Reglas contables:
- CARGO = IF(amount > 0, amount, 0.00)
- ABONO = IF(amount < 0, ABS(amount), 0.00)
"""

import logging
from pathlib import Path

import duckdb

from src.silver.domain.date_expression_ast import AmountSplitResultDTO

logger = logging.getLogger(__name__)

_NUMERIC_TYPES = {
    "DOUBLE",
    "FLOAT",
    "DECIMAL",
    "BIGINT",
    "INTEGER",
    "SMALLINT",
    "TINYINT",
    "HUGEINT",
    "REAL",
}


def _safe(path: Path) -> str:
    """Escapa comillas simples en rutas para SQL."""
    return str(path.resolve()).replace("'", "''")


def _is_numeric_type(type_str: str) -> bool:
    """Verifica si un tipo DuckDB es numérico."""
    upper = type_str.upper()
    return any(t in upper for t in _NUMERIC_TYPES)


class SilverAmountSplitterEngine:
    """Motor DuckDB nativo para separación de partida doble.

    Responsabilidades:
    - CU-04: Preview de split de columna signada a CARGO/ABONO.
    - Listado de columnas numéricas disponibles para split.
    """

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self._conn = conn

    def list_numeric_columns(self, parquet_path: str) -> list[str]:
        """Retorna nombres de columnas numéricas del Parquet."""
        pq = _safe(Path(parquet_path))
        schema = self._conn.execute(
            f"DESCRIBE SELECT * FROM read_parquet('{pq}')"
        ).fetchall()
        return [r[0] for r in schema if _is_numeric_type(r[1])]

    def preview_amount_split(
        self, parquet_path: str, source_column: str
    ) -> AmountSplitResultDTO:
        """CU-04: Calcula preview de split sin persistir cambios.

        Args:
            parquet_path: Ruta al archivo Parquet (Bronce o Plata).
            source_column: Nombre de la columna con montos signados (+/-).

        Returns:
            DTO con estadísticas del split: filas con cargo, filas con abono,
            totales monetarios de cada lado.
        """
        pq = _safe(Path(parquet_path))
        col = source_column
        query = f"""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE TRY_CAST("{col}" AS DOUBLE) > 0) AS with_cargo,
                COUNT(*) FILTER (WHERE TRY_CAST("{col}" AS DOUBLE) < 0) AS with_abono,
                COALESCE(SUM(
                    CASE WHEN TRY_CAST("{col}" AS DOUBLE) > 0
                    THEN TRY_CAST("{col}" AS DOUBLE) ELSE 0.0 END
                ), 0.0) AS sum_cargo,
                COALESCE(SUM(
                    CASE WHEN TRY_CAST("{col}" AS DOUBLE) < 0
                    THEN ABS(TRY_CAST("{col}" AS DOUBLE)) ELSE 0.0 END
                ), 0.0) AS sum_abono
            FROM read_parquet('{pq}')
        """
        row = self._conn.execute(query).fetchone()

        return AmountSplitResultDTO(
            source_column=col,
            total_rows=int(row[0]),
            rows_with_cargo=int(row[1]),
            rows_with_abono=int(row[2]),
            total_cargo=round(float(row[3]), 2),
            total_abono=round(float(row[4]), 2),
        )
