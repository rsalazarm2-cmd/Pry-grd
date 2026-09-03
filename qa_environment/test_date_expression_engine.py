"""Tests para el Motor de Expresiones de Fecha (CU-01, CU-02, CU-03)."""

from pathlib import Path
import duckdb
import pytest

from src.silver.infrastructure.silver_date_expression_engine import (
    SilverDateExpressionEngine,
)


@pytest.fixture
def conn():
    return duckdb.connect(":memory:")


@pytest.fixture
def parquet_dates_identical(conn, test_data_dir: Path) -> str:
    path = test_data_dir / "dates_identical.parquet"
    conn.execute(f"""
        COPY (
            SELECT TIMESTAMP '2026-01-15 10:00:00' AS FECHA_REGISTRO,
                   TIMESTAMP '2026-01-15 10:00:00' AS FECHA_CONTABILIZACION
            FROM generate_series(1, 100)
        ) TO '{path}' (FORMAT PARQUET)
    """)
    return str(path)


@pytest.fixture
def parquet_dates_mixed(conn, test_data_dir: Path) -> str:
    path = test_data_dir / "dates_mixed.parquet"
    conn.execute(f"""
        COPY (
            SELECT TIMESTAMP '2026-01-15 10:00:00' AS FECHA_REGISTRO,
                   CASE WHEN i <= 50 THEN TIMESTAMP '2026-01-15 10:00:00'
                   ELSE TIMESTAMP '2026-02-20 14:30:00' END AS FECHA_CONTABILIZACION
            FROM generate_series(1, 100) AS t(i)
        ) TO '{path}' (FORMAT PARQUET)
    """)
    return str(path)


@pytest.fixture
def parquet_dates_deltas(conn, test_data_dir: Path) -> str:
    path = test_data_dir / "dates_deltas.parquet"
    conn.execute(f"""
        COPY (
            SELECT * FROM (VALUES
                (TIMESTAMP '2026-01-15 10:00:00', TIMESTAMP '2026-01-15 10:00:30'),
                (TIMESTAMP '2026-01-15 10:00:00', TIMESTAMP '2026-01-15 10:00:30'),
                (TIMESTAMP '2026-01-15 10:00:00', TIMESTAMP '2026-01-15 10:01:30'),
                (TIMESTAMP '2026-01-15 10:00:00', TIMESTAMP '2026-01-15 11:00:00')
            ) AS t(FECHA_REGISTRO, FECHA_CONTABILIZACION)
        ) TO '{path}' (FORMAT PARQUET)
    """)
    return str(path)


@pytest.fixture
def parquet_weekdays(conn, test_data_dir: Path) -> str:
    path = test_data_dir / "weekdays.parquet"
    conn.execute(f"""
        COPY (
            SELECT * FROM (VALUES
                (TIMESTAMP '2026-01-12 08:00:00'), (TIMESTAMP '2026-01-13 08:00:00'),
                (TIMESTAMP '2026-01-14 08:00:00'), (TIMESTAMP '2026-01-15 08:00:00'),
                (TIMESTAMP '2026-01-16 08:00:00'), (TIMESTAMP '2026-01-17 08:00:00'),
                (TIMESTAMP '2026-01-18 08:00:00')
            ) AS t(FECHA_CONTABILIZACION)
        ) TO '{path}' (FORMAT PARQUET)
    """)
    return str(path)


# ─── CU-01: Redundancia de Fechas ───

def test_redundancy_100_percent(conn, parquet_dates_identical):
    engine = SilverDateExpressionEngine(conn)
    result = engine.compute_date_redundancy(parquet_dates_identical, "FECHA_REGISTRO", "FECHA_CONTABILIZACION")
    assert result.match_percentage == 100.0
    assert result.are_identical is True
    assert result.total_rows == 100
    assert result.matching_rows == 100


def test_redundancy_partial(conn, parquet_dates_mixed):
    engine = SilverDateExpressionEngine(conn)
    result = engine.compute_date_redundancy(parquet_dates_mixed, "FECHA_REGISTRO", "FECHA_CONTABILIZACION")
    assert result.match_percentage == 50.0
    assert result.are_identical is False
    assert result.matching_rows == 50


def test_redundancy_invalid_column(conn, parquet_dates_identical):
    engine = SilverDateExpressionEngine(conn)
    result = engine.compute_date_redundancy(parquet_dates_identical, "NO_EXISTE", "FECHA_CONTABILIZACION")
    assert result.total_rows == 0
    assert result.match_percentage == 0.0


# ─── CU-02: Delta Segundos ───

def test_delta_seconds_known_values(conn, parquet_dates_deltas):
    engine = SilverDateExpressionEngine(conn)
    result = engine.compute_date_delta(parquet_dates_deltas, "FECHA_REGISTRO", "FECHA_CONTABILIZACION")
    assert result.total_rows == 4
    assert result.min_delta_seconds == 30
    assert result.max_delta_seconds == 3600


def test_delta_rapid_approvals(conn, parquet_dates_deltas):
    engine = SilverDateExpressionEngine(conn)
    result = engine.compute_date_delta(parquet_dates_deltas, "FECHA_REGISTRO", "FECHA_CONTABILIZACION")
    assert result.rapid_approvals_count == 2


def test_delta_histogram_has_buckets(conn, parquet_dates_deltas):
    engine = SilverDateExpressionEngine(conn)
    result = engine.compute_date_delta(parquet_dates_deltas, "FECHA_REGISTRO", "FECHA_CONTABILIZACION")
    assert len(result.histogram_buckets) == 6
    labels = [b.label for b in result.histogram_buckets]
    assert "0-60s" in labels
    assert ">24h" in labels


# ─── CU-03: Día de Semana ───

def test_weekday_distribution_counts(conn, parquet_weekdays):
    engine = SilverDateExpressionEngine(conn)
    result = engine.compute_weekday_distribution(parquet_weekdays, "FECHA_CONTABILIZACION")
    assert result.total_rows == 7
    assert result.weekend_count == 2


def test_weekday_percentage(conn, parquet_weekdays):
    engine = SilverDateExpressionEngine(conn)
    result = engine.compute_weekday_distribution(parquet_weekdays, "FECHA_CONTABILIZACION")
    assert abs(result.weekend_percentage - 28.57) < 0.1


def test_weekday_distribution_has_7_days(conn, parquet_weekdays):
    engine = SilverDateExpressionEngine(conn)
    result = engine.compute_weekday_distribution(parquet_weekdays, "FECHA_CONTABILIZACION")
    assert len(result.weekday_distribution) == 7


def test_list_date_columns(conn, parquet_weekdays):
    engine = SilverDateExpressionEngine(conn)
    cols = engine.list_date_columns(parquet_weekdays)
    assert "FECHA_CONTABILIZACION" in cols
