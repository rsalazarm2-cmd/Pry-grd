import logging
import time
from pathlib import Path
import duckdb

from src.shared.domain.journal_entry import (
    SilverTransformationResultDTO,
    TabularResultDTO,
)
from src.shared.infrastructure.query_builder import QueryBuilder
from src.silver.infrastructure.duckdb_silver_query_builder import DuckDbSilverQueryBuilder
from src.shared.infrastructure.storage.atomic_parquet_writer import execute_atomic_parquet_copy
from src.silver.domain.source_risk_classifier import build_duckdb_source_risk_expression

logger = logging.getLogger(__name__)

def _safe_path(path: Path) -> str:
    return str(path.resolve()).replace("'", "''")

class SilverDuckDBService:
    """Servicio especializado de Infraestructura DuckDB para la Capa Plata."""

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def execute_ast_pipelines(
        self,
        source_path_str: str,
        target_path_str: str,
        pipelines: dict
    ) -> SilverTransformationResultDTO:
        start_time = time.time()
        source_path = Path(source_path_str).resolve()
        target_path = Path(target_path_str).resolve()

        if not source_path.exists():
            raise FileNotFoundError(f"El archivo fuente Parquet Bronce no existe en: {source_path}")

        target_path.parent.mkdir(parents=True, exist_ok=True)
        safe_source = _safe_path(source_path)
        safe_target = _safe_path(target_path)

        original_row_count = self.conn.execute(f"SELECT COUNT(*) FROM read_parquet('{safe_source}')").fetchone()[0]

        # 1. Usar el Visitor de Infraestructura para traducir los ASTs a SQL de DuckDB
        select_expressions = DuckDbSilverQueryBuilder.build_select_expressions(pipelines)

        # 2. Agregar la columna derivada TIPO_RIESGO_ORIGEN si existe ORIGEN_ASIENTO
        target_names = [p.target_name for p in pipelines.values()]
        if "ORIGEN_ASIENTO" in target_names:
            risk_expr = build_duckdb_source_risk_expression("ORIGEN_ASIENTO")
            select_expressions.append(f'({risk_expr}) AS "TIPO_RIESGO_ORIGEN"')

        # 3. Ejecutar con Escritura Atómica (temp_file -> replace)
        select_sql = f"SELECT {', '.join(select_expressions)} FROM read_parquet('{safe_source}')"
        execute_atomic_parquet_copy(self.conn, select_sql, target_path)

        silver_rows = self.conn.execute(f"SELECT COUNT(*) FROM read_parquet('{safe_target}')").fetchone()[0]

        return SilverTransformationResultDTO(
            status="success",
            source_bronze_path=str(source_path),
            target_silver_path=str(target_path),
            silver_path=str(target_path),
            original_row_count=original_row_count,
            silver_row_count=silver_rows,
            rows_processed=original_row_count,
            rows_cleaned=silver_rows,
            nulls_removed=0,
            strategy_applied="AST Pipeline & Visitor Transformation",
            columns_transformed=len(select_expressions),
            quality_summary={"OK_COMPLETO": silver_rows},
            execution_time_seconds=round(time.time() - start_time, 4),
        )

    def query_silver_records(
        self,
        silver_parquet_path: str,
        quality_status: str = None,
        limit: int = 50,
        search_term: str = None,
        column_name: str = None,
        filters_json: str = None,
        view_mode: str = "ALL",
    ) -> TabularResultDTO:
        target_path = Path(silver_parquet_path).resolve()
        if not target_path.exists():
            return TabularResultDTO(columns=[], rows=[], total_returned=0)

        total_count = self.conn.execute(f"SELECT COUNT(*) FROM read_parquet('{target_path}')").fetchone()[0]
        schema_info = self.conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{target_path}')").fetchall()
        columns = [c[0] for c in schema_info]
        col_map = {c.upper(): c for c in columns}

        where_parts: list[str] = []
        all_params: list = []

        # CU-05: Conmutación de dataset Cargos vs Abonos
        mode_upper = (view_mode or "ALL").upper()
        if mode_upper == "CARGOS":
            col_cargo = col_map.get("CARGO_MONEDA_FUNCIONAL", col_map.get("CARGO", col_map.get("ENTERED_DR")))
            if col_cargo:
                where_parts.append(f'TRY_CAST("{col_cargo}" AS DOUBLE) > 0')
        elif mode_upper == "ABONOS":
            col_abono = col_map.get("ABONO_MONEDA_FUNCIONAL", col_map.get("ABONO", col_map.get("ENTERED_CR")))
            if col_abono:
                where_parts.append(f'TRY_CAST("{col_abono}" AS DOUBLE) > 0')

        quality_sql, quality_params = QueryBuilder.build_quality_filter(quality_status)
        if quality_sql:
            where_parts.append(quality_sql)
            all_params.extend(quality_params)

        generic_where, generic_params = QueryBuilder.build_where(columns, search_term, column_name, filters_json)
        if generic_where:
            where_parts.append(generic_where.replace("WHERE ", "", 1))
            all_params.extend(generic_params)

        where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""

        query = f"SELECT * FROM read_parquet('{target_path}') {where_sql} LIMIT ?"
        all_params.append(limit)

        cursor = self.conn.execute(query, all_params)
        col_names = [desc[0] for desc in cursor.description]
        raw_rows = cursor.fetchall()
        rows = [dict(zip(col_names, r)) for r in raw_rows]

        return TabularResultDTO(
            columns=col_names,
            rows=rows,
            total_returned=total_count,
        )

