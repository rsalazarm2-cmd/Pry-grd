from abc import ABC, abstractmethod
from typing import List
from src.data_ingestion.domain.models import CatalogDTO, DatasetMetadataDTO

class CatalogPort(ABC):
    @abstractmethod
    def get_catalog(self) -> CatalogDTO:
        pass

    @abstractmethod
    def save_catalog(self, catalog: CatalogDTO) -> None:
        pass

    @abstractmethod
    def is_file_duplicate(self, file_hash: str) -> bool:
        pass

    @abstractmethod
    def register_file_hash(self, file_hash: str, dataset_name: str, partition_file: str) -> None:
        pass
