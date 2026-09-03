from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from src.shared.domain.journal_entry import SilverTransformationResultDTO, TabularResultDTO

class SilverRepository(ABC):
    """Puerto de Dominio para operaciones exclusivas de la Capa Plata."""

    @abstractmethod
    def execute_silver_ast_pipelines(self, source_path: str, target_path: str, pipelines: dict) -> SilverTransformationResultDTO:
        pass

    @abstractmethod
    def query_silver_records(
        self,
        silver_parquet_path: str,
        quality_status: Optional[str] = None,
        limit: int = 50,
        search_term: Optional[str] = None,
        column_name: Optional[str] = None,
        filters_json: Optional[str] = None,
        view_mode: Optional[str] = "ALL",
    ) -> TabularResultDTO:
        pass


    @abstractmethod
    def get_column_distinct_values(self, parquet_path: str, column_name: str) -> List[Dict[str, Any]]:
        pass
