"""Tests para el Constructor de Esquema y Reducción de Campos (CU-06).

Valida que:
1. La selección de N columnas crudas en Bronce se reduzca correctamente a M en Plata.
2. Las columnas renombradas tomen los nombres canónicos especificados.
3. El Visitor DuckDB genere el SELECT exacto de acuerdo con las reglas.
"""

from pathlib import Path
import duckdb
import pytest

from src.bronze.domain.pipeline import TransformationPipelineBuilder
from src.silver.infrastructure.duckdb_silver_query_builder import DuckDbSilverQueryBuilder
from src.shared.domain.journal_entry import BronzeToSilverRulesDTO, ColumnCleaningRuleDTO


@pytest.fixture
def conn():
    return duckdb.connect(":memory:")


@pytest.fixture
def bronze_parquet(conn, test_data_dir: Path) -> str:
    """Crea un Parquet de prueba con 5 columnas crudas."""
    path = test_data_dir / "bronze_schema_test.parquet"
    conn.execute(f"""
        COPY (
            SELECT
                1001 AS JE_HEADER_ID,
                'Sales' AS JE_CATEGORY,
                1500.50 AS ENTERED_DR,
                0.00 AS ENTERED_CR,
                'IGNORED_COL' AS EXTRA_DATA
            FROM generate_series(1, 10)
        ) TO '{path}' (FORMAT PARQUET)
    """)
    return str(path)


def test_schema_reduction_n_to_m():
    """Verifica la reducción de 5 columnas a 3 en el pipeline AST."""
    rules = BronzeToSilverRulesDTO(
        column_rules={
            "JE_HEADER_ID": ColumnCleaningRuleDTO(include_in_silver=True, new_column_name="FOLIO_ASIENTO"),
            "JE_CATEGORY": ColumnCleaningRuleDTO(include_in_silver=True, new_column_name="CATEGORIA_ASIENTO"),
            "ENTERED_DR": ColumnCleaningRuleDTO(include_in_silver=True, new_column_name="CARGO_MONEDA_ORIGINAL"),
            "ENTERED_CR": ColumnCleaningRuleDTO(include_in_silver=False),
            "EXTRA_DATA": ColumnCleaningRuleDTO(include_in_silver=False),
        }
    )
    cols = ["JE_HEADER_ID", "JE_CATEGORY", "ENTERED_DR", "ENTERED_CR", "EXTRA_DATA"]
    pipelines = TransformationPipelineBuilder.build_from_dto(rules, cols)

    assert len(pipelines) == 3
    assert "JE_HEADER_ID" in pipelines
    assert pipelines["JE_HEADER_ID"].target_name == "FOLIO_ASIENTO"
    assert "EXTRA_DATA" not in pipelines


def test_visitor_generates_valid_sql(conn, bronze_parquet):
    """Verifica que el QueryBuilder construya sentencias SQL ejecutables en DuckDB."""
    rules = BronzeToSilverRulesDTO(
        column_rules={
            "JE_HEADER_ID": ColumnCleaningRuleDTO(include_in_silver=True, new_column_name="FOLIO"),
            "JE_CATEGORY": ColumnCleaningRuleDTO(include_in_silver=True, new_column_name="CATEGORIA"),
        }
    )
    cols = ["JE_HEADER_ID", "JE_CATEGORY"]
    pipelines = TransformationPipelineBuilder.build_from_dto(rules, cols)
    select_exprs = DuckDbSilverQueryBuilder.build_select_expressions(pipelines)

    sql = f"SELECT {', '.join(select_exprs)} FROM read_parquet('{bronze_parquet}')"
    rows = conn.execute(sql).fetchall()

    assert len(rows) == 10
    cols_result = [d[0] for d in conn.execute(sql).description]
    assert cols_result == ["FOLIO", "CATEGORIA"]


def test_query_silver_records_view_mode(conn, test_data_dir: Path):
    """CU-05: Verifica el filtrado de view_mode (CARGOS vs ABONOS)."""
    from src.silver.infrastructure.silver_service import SilverDuckDBService

    path = str(test_data_dir / "view_mode_test.parquet")
    conn.execute(f"""
        COPY (
            SELECT * FROM (VALUES
                (100.0, 0.0),
                (0.0, 50.0),
                (200.0, 0.0)
            ) AS t(CARGO_MONEDA_FUNCIONAL, ABONO_MONEDA_FUNCIONAL)
        ) TO '{path}' (FORMAT PARQUET)
    """)

    service = SilverDuckDBService(conn)
    all_res = service.query_silver_records(path, view_mode="ALL")
    cargos_res = service.query_silver_records(path, view_mode="CARGOS")
    abonos_res = service.query_silver_records(path, view_mode="ABONOS")

    assert len(all_res.rows) == 3
    assert len(cargos_res.rows) == 2
    assert len(abonos_res.rows) == 1

