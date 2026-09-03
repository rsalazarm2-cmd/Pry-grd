"""Tests para el Motor de Separación de Partida Doble (CU-04).

Genera datos sintéticos en Parquet con montos positivos, negativos y cero
para validar la separación en CARGO (>0) y ABONO (<0 → abs).
"""

import pytest
from pathlib import Path

import duckdb

from src.silver.infrastructure.silver_amount_splitter_engine import (
    SilverAmountSplitterEngine,
)


@pytest.fixture
def conn():
    """Conexión DuckDB in-memory para tests."""
    return duckdb.connect(":memory:")


@pytest.fixture
def parquet_amounts(conn, test_data_dir: Path) -> str:
    """Crea Parquet con montos signados conocidos: +1000, -500, 0, +250, -750."""
    path = test_data_dir / "amounts.parquet"
    conn.execute(f"""
        COPY (
            SELECT * FROM (VALUES
                (1000.00,  'Cargo normal'),
                (-500.00,  'Abono normal'),
                (0.00,     'Sin movimiento'),
                (250.50,   'Cargo fraccionado'),
                (-750.25,  'Abono grande')
            ) AS t(MONTO, DESCRIPCION)
        ) TO '{path}' (FORMAT PARQUET)
    """)
    return str(path)


@pytest.fixture
def parquet_all_positive(conn, test_data_dir: Path) -> str:
    """Crea Parquet donde todos los montos son positivos."""
    path = test_data_dir / "all_positive.parquet"
    conn.execute(f"""
        COPY (
            SELECT * FROM (VALUES (100.0), (200.0), (300.0)) AS t(IMPORTE)
        ) TO '{path}' (FORMAT PARQUET)
    """)
    return str(path)


# ─── CU-04: Split Cargo/Abono ───


def test_split_positive_to_cargo(conn, parquet_amounts):
    """Montos positivos deben ir a CARGO."""
    engine = SilverAmountSplitterEngine(conn)
    result = engine.preview_amount_split(parquet_amounts, "MONTO")
    assert result.rows_with_cargo == 2  # +1000.00 y +250.50


def test_split_negative_to_abono(conn, parquet_amounts):
    """Montos negativos deben ir a ABONO (valor absoluto)."""
    engine = SilverAmountSplitterEngine(conn)
    result = engine.preview_amount_split(parquet_amounts, "MONTO")
    assert result.rows_with_abono == 2  # -500.00 y -750.25


def test_split_zero_stays_zero(conn, parquet_amounts):
    """El monto 0 no cuenta ni como cargo ni como abono."""
    engine = SilverAmountSplitterEngine(conn)
    result = engine.preview_amount_split(parquet_amounts, "MONTO")
    # Total = 5, cargo = 2, abono = 2, cero = 1
    assert result.total_rows == 5
    assert result.rows_with_cargo + result.rows_with_abono == 4


def test_split_totals_match(conn, parquet_amounts):
    """sum(CARGO) + sum(ABONO) == sum(abs(original)) para no-cero."""
    engine = SilverAmountSplitterEngine(conn)
    result = engine.preview_amount_split(parquet_amounts, "MONTO")
    # CARGO: 1000.00 + 250.50 = 1250.50
    # ABONO: 500.00 + 750.25 = 1250.25
    assert abs(result.total_cargo - 1250.50) < 0.01
    assert abs(result.total_abono - 1250.25) < 0.01


def test_split_all_positive(conn, parquet_all_positive):
    """Si todos son positivos, abono debe ser 0."""
    engine = SilverAmountSplitterEngine(conn)
    result = engine.preview_amount_split(parquet_all_positive, "IMPORTE")
    assert result.rows_with_abono == 0
    assert result.total_abono == 0.0
    assert result.rows_with_cargo == 3


def test_list_numeric_columns(conn, parquet_amounts):
    """Debe detectar MONTO como columna numérica."""
    engine = SilverAmountSplitterEngine(conn)
    cols = engine.list_numeric_columns(parquet_amounts)
    assert "MONTO" in cols


def test_list_numeric_excludes_text(conn, parquet_amounts):
    """DESCRIPCION (VARCHAR) no debe aparecer en columnas numéricas."""
    engine = SilverAmountSplitterEngine(conn)
    cols = engine.list_numeric_columns(parquet_amounts)
    assert "DESCRIPCION" not in cols
