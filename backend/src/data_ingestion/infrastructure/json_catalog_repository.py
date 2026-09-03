import json
from pathlib import Path
from typing import Dict, List
from src.data_ingestion.domain.catalog_port import CatalogPort
from src.data_ingestion.domain.models import CatalogDTO, DatasetMetadataDTO, ColumnSchemaDTO

class JsonCatalogRepository(CatalogPort):
    def __init__(self, catalog_path: str, project_id: str):
        self.catalog_path = Path(catalog_path)
        self.project_id = project_id
        # El manifiesto de hashes para evitar duplicados
        self.hashes_path = self.catalog_path.parent / ".ingestion_hashes.json"

    def get_catalog(self) -> CatalogDTO:
        if not self.catalog_path.exists():
            return CatalogDTO(project_id=self.project_id, datasets={})
        
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return CatalogDTO(**data)

    def save_catalog(self, catalog: CatalogDTO) -> None:
        self.catalog_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.catalog_path, "w", encoding="utf-8") as f:
            json.dump(catalog.dict(), f, indent=4)

    def _get_hashes(self) -> Dict[str, dict]:
        if not self.hashes_path.exists():
            return {}
        with open(self.hashes_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def is_file_duplicate(self, file_hash: str) -> bool:
        hashes = self._get_hashes()
        return file_hash in hashes

    def register_file_hash(self, file_hash: str, dataset_name: str, partition_file: str) -> None:
        hashes = self._get_hashes()
        hashes[file_hash] = {
            "dataset": dataset_name,
            "partition": partition_file
        }
        self.hashes_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.hashes_path, "w", encoding="utf-8") as f:
            json.dump(hashes, f, indent=4)
