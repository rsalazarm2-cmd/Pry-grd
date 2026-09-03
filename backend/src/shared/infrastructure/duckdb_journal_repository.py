import duckdb
from typing import Any, Dict, List, Optional
from pathlib import Path

from src.shared.domain.journal_entry import (
    BronzeIngestionResultDTO,
    DatasetProfileDTO,
    GoldModelsResultDTO,
    SilverTransformationResultDTO,
    TabularResultDTO,
)
from src.shared.domain.journal_entry_repository import JournalEntryRepository
from src.shared.infrastructure.engine import DuckDBEngine
from src.bronze.infrastructure.bronze_service import BronzeDuckDBService
from src.silver.infrastructure.silver_service import SilverDuckDBService
from src.gold.infrastructure.gold_service import GoldDuckDBService


class DuckDBJournalRepository(JournalEntryRepository):
    """
    Adaptador concreto de Infraestructura que implementa JournalEntryRepository
    delegando en los servicios especializados de DuckDB (Bronce, Plata, Oro).
    """

    def __init__(self, db_connection: duckdb.DuckDBPyConnection = None):
        self.engine = DuckDBEngine(db_connection)
        self.conn = self.engine.get_connection()
        self.bronze_service = BronzeDuckDBService(self.conn)
        self.silver_service = SilverDuckDBService(self.conn)
        self.gold_service = GoldDuckDBService(self.conn)

    def save_bronze(self, source_csv_path: str, target_parquet_path: str) -> BronzeIngestionResultDTO:
        return self.bronze_service.save_bronze(source_csv_path, target_parquet_path)

    def get_bronze_profile(self, bronze_parquet_path: str) -> DatasetProfileDTO:
        return self.bronze_service.get_bronze_profile(bronze_parquet_path)

    def get_parquet_schema(self, parquet_path: str) -> list[str]:
        path_obj = Path(parquet_path).resolve()
        safe_path = str(path_obj).replace("'", "''")
        rows = self.conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{safe_path}')").fetchall()
        return [r[0] for r in rows]

    def execute_silver_ast_pipelines(self, source_path: str, target_path: str, pipelines: dict) -> SilverTransformationResultDTO:
        return self.silver_service.execute_ast_pipelines(source_path, target_path, pipelines)

    def execute_gold_models(
        self, 
        silver_parquet_path: str, 
        target_gold_dir: str, 
        enriched_expressions: List[str], 
        metadata: Dict[str, Any]
    ) -> GoldModelsResultDTO:
        return self.gold_service.execute_gold_models(silver_parquet_path, target_gold_dir, enriched_expressions, metadata)

    def query_bronze_records(
        self,
        bronze_parquet_path: str,
        limit: int = 50,
        search_term: str = None,
        column_name: str = None,
        filters_json: str = None,
    ) -> TabularResultDTO:
        return self.bronze_service.query_bronze_records(bronze_parquet_path, limit, search_term, column_name, filters_json)

    def get_bronze_records(self, *args, **kwargs) -> TabularResultDTO:
        """Alias de compatibilidad para query_bronze_records."""
        return self.query_bronze_records(*args, **kwargs)

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
        return self.silver_service.query_silver_records(
            silver_parquet_path, quality_status, limit, search_term, column_name, filters_json, view_mode
        )


    def get_silver_records(self, *args, **kwargs) -> TabularResultDTO:
        """Alias de compatibilidad para query_silver_records."""
        return self.query_silver_records(*args, **kwargs)

    def query_gold_balances(
        self,
        gold_parquet_path: str,
        search_term: str = None,
        column_name: str = None,
        filters_json: str = None,
    ) -> TabularResultDTO:
        return self.gold_service.query_gold_balances(gold_parquet_path, search_term, column_name, filters_json)

    def get_gold_balances(self, *args, **kwargs) -> TabularResultDTO:
        """Alias de compatibilidad para query_gold_balances."""
        return self.query_gold_balances(*args, **kwargs)

    def query_gold_account_balances(
        self,
        gold_account_parquet_path: str,
        search_term: str = None,
        column_name: str = None,
        filters_json: str = None,
    ) -> TabularResultDTO:
        return self.gold_service.query_gold_account_balances(gold_account_parquet_path, search_term, column_name, filters_json)

    def get_gold_account_balances(self, *args, **kwargs) -> TabularResultDTO:
        """Alias de compatibilidad para query_gold_account_balances."""
        return self.query_gold_account_balances(*args, **kwargs)

    def get_column_distinct_values(self, parquet_path: str, column_name: str) -> List[Dict[str, Any]]:
        path_obj = Path(parquet_path).resolve()
        safe_path = str(path_obj).replace("'", "''")
        safe_col = column_name.replace('"', '""')
        
        query = f"""
            SELECT "{safe_col}" AS value, COUNT(*) AS count 
            FROM read_parquet('{safe_path}') 
            WHERE "{safe_col}" IS NOT NULL 
            GROUP BY "{safe_col}" 
            ORDER BY count DESC 
            LIMIT 50
        """
        try:
            rows = self.conn.execute(query).fetchall()
            return [{"value": str(r[0]), "count": r[1]} for r in rows]
        except Exception:
            return []
