"""Servicio de Linaje y Trazabilidad Transparente de Mapeo (CU-07).

Construye la matriz de linaje comparando las columnas de la Capa Bronce,
las reglas aplicadas (o guardadas en .column_mapping_rules.json) y la Capa Plata.
"""

import logging
from pathlib import Path
import duckdb

from src.silver.domain.lineage_dto import LineageItemDTO, LineageMatrixDTO
from src.bronze.infrastructure.mapping_rules_persistence_service import (
    MappingRulesPersistenceService,
)

logger = logging.getLogger(__name__)


def _safe(path: Path) -> str:
    return str(path.resolve()).replace("'", "''")


class SilverLineageService:
    """Calcula y construye la matriz de trazabilidad transparente Origen ➔ Plata."""

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self._conn = conn

    def get_lineage_matrix(
        self, bronze_path: Path, silver_path: Path, project_id: str = "proyecto-principal"
    ) -> LineageMatrixDTO:
        """Calcula el linaje de columnas de Bronce a Plata."""
        if not bronze_path.exists():
            return LineageMatrixDTO(project_id=project_id)

        safe_b = _safe(bronze_path)
        bronze_schema = self._conn.execute(
            f"DESCRIBE SELECT * FROM read_parquet('{safe_b}')"
        ).fetchall()

        bronze_cols = {r[0]: r[1] for r in bronze_schema}
        saved_rules = MappingRulesPersistenceService.load_saved_rules(bronze_path)

        silver_cols = {}
        if silver_path.exists():
            safe_s = _safe(silver_path)
            silver_schema = self._conn.execute(
                f"DESCRIBE SELECT * FROM read_parquet('{safe_s}')"
            ).fetchall()
            silver_cols = {r[0]: r[1] for r in silver_schema}

        items: list[LineageItemDTO] = []
        for b_col, b_type in bronze_cols.items():
            rule = saved_rules.column_rules.get(b_col) if saved_rules else None
            is_inc = rule.include_in_silver if rule else True
            t_col = rule.new_column_name if (rule and rule.new_column_name) else b_col
            t_type = rule.target_data_type if (rule and rule.target_data_type) else silver_cols.get(t_col, b_type)
            imputation = rule.null_imputation if rule else "DEFAULT"

            items.append(
                LineageItemDTO(
                    source_column=b_col,
                    target_column=t_col,
                    inferred_type=b_type,
                    target_type=t_type,
                    null_imputation=imputation,
                    is_included=is_inc,
                    quality_status="OK" if is_inc else "EXCLUDED",
                )
            )

        return LineageMatrixDTO(
            project_id=project_id,
            source_columns_count=len(bronze_cols),
            target_columns_count=len(silver_cols) if silver_cols else len([i for i in items if i.is_included]),
            recipe_applied=saved_rules is not None,
            items=items,
        )
