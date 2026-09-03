from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.shared.domain.journal_entry import (


    BronzeIngestionResultDTO,
    DatasetProfileDTO,
    GoldModelsResultDTO,
    SilverTransformationResultDTO,
    TabularResultDTO,
    TransformationRulesDTO,
)


class JournalEntryRepository(ABC):
    """
    Puerto (Port) de la Arquitectura Hexagonal para el acceso y transformación de datos.
    Cero dependencia de DuckDB, Django u ORMs.
    """

    @abstractmethod
    def save_bronze(self, source_csv_path: str, target_parquet_path: str) -> BronzeIngestionResultDTO:
        """Ingesta el archivo CSV crudo y genera el archivo Parquet para la Capa Bronce."""
        pass

    @abstractmethod
    def get_bronze_profile(self, bronze_parquet_path: str) -> DatasetProfileDTO:
        """Calcula el perfilamiento de columnas, nulos y tipos sobre la Capa Bronce."""
        pass

    @abstractmethod
    def get_parquet_schema(self, parquet_path: str) -> list[str]:
        """Devuelve la lista de nombres de columnas de un archivo Parquet."""
        pass

    @abstractmethod
    def execute_silver_ast_pipelines(self, source_path: str, target_path: str, pipelines: dict) -> SilverTransformationResultDTO:
        """Ejecuta los AST pipelines previamente armados por el dominio en la infraestructura destino."""
        pass

    @abstractmethod
    def execute_gold_models(self, silver_parquet_path: str, target_gold_dir: str, enriched_expressions: List[str], metadata: Dict[str, Any]) -> GoldModelsResultDTO:
        """Genera datamarts en la Capa Oro usando un AST previamente calculado por el Dominio."""
        pass

    @abstractmethod
    def get_bronze_records(
        self, bronze_parquet_path: str, limit: int = 50, search: str = None, column_name: str = None, filters_json: str = None
    ) -> TabularResultDTO:
        """Consulta registros crudos de la Capa Bronce con soporte de búsqueda y filtros multi-valor."""
        pass

    @abstractmethod
    def get_silver_records(
        self,
        silver_parquet_path: str,
        quality_status: str = None,
        limit: int = 50,
        search: str = None,
        column_name: str = None,
        filters_json: str = None,
        view_mode: str = "ALL",
    ) -> TabularResultDTO:
        """Consulta registros de la Capa Plata con filtro opcional por QUALITY_STATUS, búsqueda, filtros multi-valor y view_mode (CU-05)."""
        pass


    @abstractmethod
    def get_gold_balances(self, gold_parquet_path: str, search: str = None, column_name: str = None, filters_json: str = None) -> TabularResultDTO:
        """Consulta la tabla de balances agregados por libro de la Capa Oro."""
        pass

    @abstractmethod
    def get_gold_account_balances(self, gold_account_parquet_path: str, search: str = None, column_name: str = None, filters_json: str = None) -> TabularResultDTO:
        """Consulta la tabla de balances por cuenta natural (PyG) de la Capa Oro."""
        pass

    @abstractmethod
    def get_column_distinct_values(self, layer_parquet_path: str, column_name: str) -> list:
        """Obtiene la lista de valores únicos y su conteo de frecuencias para poblar los filtros estilo Excel."""
        pass

