from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from src.shared.domain.journal_entry import GoldModelsResultDTO, TabularResultDTO

class GoldRepository(ABC):
    """Puerto de Dominio para operaciones exclusivas de la Capa Oro."""

    @abstractmethod
    def execute_gold_models(
        self, 
        silver_parquet_path: str, 
        target_gold_dir: str, 
        enriched_expressions: List[str], 
        metadata: Dict[str, Any]
    ) -> GoldModelsResultDTO:
        pass

    @abstractmethod
    def query_gold_balances(
        self,
        gold_parquet_path: str,
        search_term: Optional[str] = None,
        column_name: Optional[str] = None,
        filters_json: Optional[str] = None,
    ) -> TabularResultDTO:
        pass

    @abstractmethod
    def query_gold_account_balances(
        self,
        gold_account_parquet_path: str,
        search_term: Optional[str] = None,
        column_name: Optional[str] = None,
        filters_json: Optional[str] = None,
    ) -> TabularResultDTO:
        pass

    @abstractmethod
    def get_column_distinct_values(self, parquet_path: str, column_name: str) -> List[Dict[str, Any]]:
        pass
