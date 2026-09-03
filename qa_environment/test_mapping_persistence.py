"""Tests para la Persistencia Inmutable de Reglas de Mapeo (CU-08).

Valida que:
1. Las reglas de mapeo se guarden en .column_mapping_rules.json.
2. Las reglas guardadas se recarguen en ~1 ms.
3. El linaje calcule la matriz correctamente usando las reglas guardadas.
"""

from pathlib import Path
import time
import duckdb
import pytest

from src.bronze.infrastructure.mapping_rules_persistence_service import (
    MappingRulesPersistenceService,
)
from src.silver.infrastructure.silver_lineage_service import SilverLineageService
from src.shared.domain.journal_entry import BronzeToSilverRulesDTO, ColumnCleaningRuleDTO


@pytest.fixture
def conn():
    return duckdb.connect(":memory:")


@pytest.fixture
def bronze_file(test_data_dir: Path) -> Path:
    p = test_data_dir / "bronze_persist_test.parquet"
    conn = duckdb.connect(":memory:")
    conn.execute(f"COPY (SELECT 1 AS ID, 'A' AS TEXTO) TO '{p}' (FORMAT PARQUET)")
    return p


def test_rules_save_and_load_in_1ms(bronze_file: Path):
    """Guarda y recarga las reglas comprobando la persistencia y velocidad."""
    rules = BronzeToSilverRulesDTO(
        column_rules={
            "ID": ColumnCleaningRuleDTO(include_in_silver=True, new_column_name="FOLIO"),
            "TEXTO": ColumnCleaningRuleDTO(include_in_silver=False),
        }
    )

    MappingRulesPersistenceService.save_rules(bronze_file, rules)
    rules_path = MappingRulesPersistenceService.get_rules_path(bronze_file)
    assert rules_path.exists()

    t0 = time.time()
    loaded = MappingRulesPersistenceService.load_saved_rules(bronze_file)
    elapsed_ms = (time.time() - t0) * 1000

    assert loaded is not None
    assert loaded.column_rules["ID"].new_column_name == "FOLIO"
    assert loaded.column_rules["TEXTO"].include_in_silver is False
    assert elapsed_ms < 50.0  # < 50ms (típicamente ~1ms)


def test_lineage_matrix_uses_saved_rules(conn, bronze_file: Path):
    """Verifica que el servicio de linaje consuma las reglas guardadas."""
    silver_path = bronze_file.parent / "silver_test.parquet"
    conn.execute(f"COPY (SELECT 1 AS FOLIO) TO '{silver_path}' (FORMAT PARQUET)")

    rules = BronzeToSilverRulesDTO(
        column_rules={
            "ID": ColumnCleaningRuleDTO(include_in_silver=True, new_column_name="FOLIO"),
            "TEXTO": ColumnCleaningRuleDTO(include_in_silver=False),
        }
    )
    MappingRulesPersistenceService.save_rules(bronze_file, rules)

    service = SilverLineageService(conn)
    matrix = service.get_lineage_matrix(bronze_file, silver_path, project_id="test-proj")

    assert matrix.recipe_applied is True
    assert matrix.source_columns_count == 2
    items_by_src = {item.source_column: item for item in matrix.items}
    assert items_by_src["ID"].target_column == "FOLIO"
    assert items_by_src["TEXTO"].is_included is False
