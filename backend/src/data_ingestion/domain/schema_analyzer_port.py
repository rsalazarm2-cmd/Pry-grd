from abc import ABC, abstractmethod
from typing import List
from src.data_ingestion.domain.models import ColumnSchemaDTO

class SchemaAnalyzerPort(ABC):
    @abstractmethod
    def extract_schema(self, file_path: str) -> List[ColumnSchemaDTO]:
        """Extrae la lista de columnas y sus tipos de datos de un archivo crudo."""
        pass

    @abstractmethod
    def convert_to_parquet(self, source_csv_path: str, target_parquet_path: str, types_coercion: dict = None) -> int:
        """Convierte el archivo a Parquet forzando tipos si es necesario, retorna número de filas."""
        pass
