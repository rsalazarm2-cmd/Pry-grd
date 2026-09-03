"""Pruebas Unitarias para el Analizador Forense de la Ley de Benford."""

import duckdb
import pytest
from src.audit.infrastructure.benford_analyzer import BenfordAnalyzer


@pytest.fixture
def memory_duckdb_benford_data():
    """Fixture con una tabla DuckDB que simula una distribución natural de Benford."""
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE TABLE sample_amounts (CARGO_MONEDA_FUNCIONAL DOUBLE)")

    # Insertar montos comenzando con 1, 2, 3...
    values = []
    # 1 -> ~30%
    for _ in range(30):
        values.append("(1500.00)")
        values.append("(190.00)")
    # 2 -> ~17%
    for _ in range(17):
        values.append("(2500.00)")
        values.append("(210.00)")
    # 3 -> ~12%
    for _ in range(12):
        values.append("(3400.00)")
    # 4 -> ~10%
    for _ in range(10):
        values.append("(4200.00)")
    # 5..9 -> resto
    for _ in range(31):
        values.append("(8500.00)")

    conn.execute(f"INSERT INTO sample_amounts VALUES {', '.join(values)}")
    return conn


def test_benford_analyzer_first_digit(memory_duckdb_benford_data):
    """Verifica que el analizador calcule las frecuencias observadas del 1er dígito."""
    analyzer = BenfordAnalyzer(memory_duckdb_benford_data)
    result = analyzer.analyze_column("sample_amounts", "CARGO_MONEDA_FUNCIONAL")

    assert result.total_samples > 0
    assert len(result.first_digit_analysis) == 9
    assert len(result.second_digit_analysis) == 10

    digit_1 = next(d for d in result.first_digit_analysis if d.digit == 1)
    assert digit_1.expected_freq == 30.1
    assert digit_1.actual_count > 0
