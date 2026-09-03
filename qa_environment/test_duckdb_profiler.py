"""Pruebas Unitarias para el Motor de Profiling Empírico DuckDB y Veto de Categorías."""

import os
import duckdb
import pytest
from src.ai_translator.infrastructure.duckdb_profiler import DuckDBProfiler
from src.ai_translator.infrastructure.fuzzy_forensic_nlp import FuzzyForensicNLPClassifier


@pytest.fixture
def sample_parquet_file(tmp_path):
    """Crea un archivo Parquet de prueba con unicidad variable (PK única vs Categoría)."""
    parquet_path = str(tmp_path / "test_data.parquet")
    conn = duckdb.connect()
    conn.execute("""
        CREATE TABLE dummy AS SELECT 
            'ASIENTO_' || range AS FOLIO_ASIENTO,
            CASE WHEN range % 2 = 0 THEN 'MANUAL' ELSE 'COMPRAS' END AS CATEGORIA_ASIENTO,
            range * 100.0 AS CARGO_MONEDA_FUNCIONAL
        FROM range(1, 101)
    """)
    conn.execute(f"COPY dummy TO '{parquet_path}' (FORMAT PARQUET)")
    conn.close()
    return parquet_path


def test_duckdb_profiler_uniqueness_ratios(sample_parquet_file):
    """Verifica que el profiler reconozca FOLIO_ASIENTO como PK única y CATEGORIA_ASIENTO como categoría."""
    profiler = DuckDBProfiler()
    metrics = profiler.profile_parquet_columns(
        sample_parquet_file, ["FOLIO_ASIENTO", "CATEGORIA_ASIENTO", "CARGO_MONEDA_FUNCIONAL"]
    )

    folio_m = metrics["FOLIO_ASIENTO"]
    assert folio_m.uniqueness_ratio == 1.0
    assert folio_m.is_unique_key_candidate is True
    assert folio_m.is_low_cardinality_category is False

    cat_m = metrics["CATEGORIA_ASIENTO"]
    assert cat_m.uniqueness_ratio == 0.02  # 2 distintas de 100 filas
    assert cat_m.is_unique_key_candidate is False
    assert cat_m.is_low_cardinality_category is True


def test_fuzzy_nlp_empirical_veto(sample_parquet_file):
    """Verifica que la categoría de baja cardinalidad sea vetada como PK por el NLP."""
    profiler = DuckDBProfiler()
    metrics = profiler.profile_parquet_columns(
        sample_parquet_file, ["CATEGORIA_ASIENTO"]
    )

    classifier = FuzzyForensicNLPClassifier()
    res = classifier.classify_column("CATEGORIA_ASIENTO", metrics["CATEGORIA_ASIENTO"])

    assert res.vector_category != "ACCOUNTING"
    assert "Veto Empírico" in res.rationale
