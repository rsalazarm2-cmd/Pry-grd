from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from src.shared.domain.journal_entry import BronzeIngestionResultDTO, DatasetProfileDTO, TabularResultDTO

class BronzeRepository(ABC):
    """Puerto de Dominio para operaciones exclusivas de la Capa Bronce."""

    @abstractmethod
    def save_bronze(self, source_csv_path: str, target_parquet_path: str) -> BronzeIngestionResultDTO:
        pass

    @abstractmethod
    def get_bronze_profile(self, bronze_parquet_path: str) -> DatasetProfileDTO:
        pass

    @abstractmethod
    def query_bronze_records(
        self,
        bronze_parquet_path: str,
        limit: int = 50,
        search_term: Optional[str] = None,
        column_name: Optional[str] = None,
        filters_json: Optional[str] = None,
    ) -> TabularResultDTO:
        pass

    @abstractmethod
    def get_column_distinct_values(self, parquet_path: str, column_name: str) -> List[Dict[str, Any]]:
        pass
