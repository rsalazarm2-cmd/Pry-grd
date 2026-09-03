import logging
import time
from pathlib import Path
from typing import Any, Dict, List
import duckdb

from src.shared.domain.journal_entry import TabularResultDTO
from src.shared.infrastructure.query_builder import QueryBuilder

logger = logging.getLogger(__name__)

class GoldDuckDBService:
    """Servicio especializado de Infraestructura DuckDB para la Capa Oro y Analítica BI."""

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn



    def query_gold_balances(
        self, gold_parquet_path: str, search_term: str = None, column_name: str = None, filters_json: str = None
    ) -> TabularResultDTO:
        target_path = Path(gold_parquet_path).resolve()
        if not target_path.exists():
            return TabularResultDTO(total_count=0, returned_count=0, columns=[], rows=[])

        total_count = self.conn.execute(f"SELECT COUNT(*) FROM read_parquet('{target_path}')").fetchone()[0]
        schema_info = self.conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{target_path}')").fetchall()
        columns = [c[0] for c in schema_info]

        where_sql, params = QueryBuilder.build_where(columns, search_term, column_name, filters_json)
        query = f"SELECT * FROM read_parquet('{target_path}') {where_sql}"

        cursor = self.conn.execute(query, params)
        col_names = [desc[0] for desc in cursor.description]
        raw_rows = cursor.fetchall()
        rows = [dict(zip(col_names, r)) for r in raw_rows]

        return TabularResultDTO(
            total_count=total_count,
            returned_count=len(rows),
            columns=col_names,
            rows=rows,
        )

    def query_gold_account_balances(
        self, gold_account_parquet_path: str, search_term: str = None, column_name: str = None, filters_json: str = None
    ) -> TabularResultDTO:
        return self.query_gold_balances(gold_account_parquet_path, search_term, column_name, filters_json)

    def get_column_distinct_values(self, parquet_path: str, column_name: str) -> List[Dict[str, Any]]:
        target_path = Path(parquet_path).resolve()
        if not target_path.exists():
            return []

        schema_info = self.conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{target_path}')").fetchall()
        valid_cols = [c[0] for c in schema_info]
        validated_col = QueryBuilder.validate_column(column_name, valid_cols)
        if not validated_col:
            return []

        query = f"""
            SELECT CAST("{validated_col}" AS VARCHAR) AS val, COUNT(*) AS cnt
            FROM read_parquet('{target_path}')
            GROUP BY "{validated_col}"
            ORDER BY cnt DESC, val ASC LIMIT 500
        """
        rows = self.conn.execute(query).fetchall()
        return [{"value": r[0] if r[0] is not None else "NULL", "count": r[1]} for r in rows]
