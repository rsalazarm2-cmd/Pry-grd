import duckdb
from typing import List, Dict
from src.data_ingestion.domain.schema_analyzer_port import SchemaAnalyzerPort
from src.data_ingestion.domain.models import ColumnSchemaDTO

class DuckDBSchemaAnalyzer(SchemaAnalyzerPort):
    """Analiza esquemas de CSV y convierte a Parquet preservando el tipo crudo (VARCHAR) en Capa Bronce."""
    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def extract_schema(self, file_path: str) -> List[ColumnSchemaDTO]:
        query = f"DESCRIBE SELECT * FROM read_csv_auto('{file_path}', all_varchar=True)"
        rows = self.conn.execute(query).fetchall()
        schema = []
        for row in rows:
            col_name = row[0]
            col_type = row[1]
            schema.append(ColumnSchemaDTO(name=col_name, data_type=col_type))
        return schema

    def convert_to_parquet(self, source_csv_path: str, target_parquet_path: str, types_coercion: Dict[str, str] = None) -> int:
        read_expr = f"read_csv_auto('{source_csv_path}', all_varchar=True)"
        copy_query = f"""
            COPY (SELECT * FROM {read_expr})
            TO '{target_parquet_path}' (FORMAT PARQUET)
        """
        self.conn.execute(copy_query)
        count_query = f"SELECT count(*) FROM {read_expr}"
        rows_inserted = self.conn.execute(count_query).fetchone()[0]
        return rows_inserted
