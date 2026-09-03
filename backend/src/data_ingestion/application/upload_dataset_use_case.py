import hashlib
import time
from pathlib import Path
from typing import List, Optional
import uuid
from datetime import datetime

from src.data_ingestion.domain.models import (
    IngestionResultDTO,
    IngestionDecisionDTO,
    IngestionAction,
    DatasetMetadataDTO,
    ColumnSchemaDTO
)
from src.data_ingestion.domain.catalog_port import CatalogPort
from src.data_ingestion.domain.schema_analyzer_port import SchemaAnalyzerPort

class UploadDatasetUseCase:
    def __init__(self, catalog_repo: CatalogPort, schema_analyzer: SchemaAnalyzerPort):
        self.catalog_repo = catalog_repo
        self.schema_analyzer = schema_analyzer

    def _hash_file(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def _compare_schemas(self, incoming: List[ColumnSchemaDTO], existing: List[ColumnSchemaDTO]) -> bool:
        """Compara si dos esquemas son estructuralmente iguales en nombres de columnas."""
        if len(incoming) != len(existing):
            return False
        
        # Comparar nombres (podemos ser case insensitive si lo deseamos, pero por ahora exacto)
        inc_names = [c.name for c in incoming]
        ex_names = [c.name for c in existing]
        return inc_names == ex_names

    def _get_coercion_types(self, incoming: List[ColumnSchemaDTO], existing: List[ColumnSchemaDTO]) -> dict:
        """Si los nombres son iguales pero los tipos cambian, forzamos al tipo original."""
        coercion = {}
        for inc, ex in zip(incoming, existing):
            if inc.name == ex.name and inc.data_type != ex.data_type:
                coercion[ex.name] = ex.data_type
        return coercion

    def execute(self, source_csv_path: str, bronze_base_dir: str) -> IngestionResultDTO:
        file_hash = self._hash_file(source_csv_path)
        
        # 1. Validación de Duplicados
        if self.catalog_repo.is_file_duplicate(file_hash):
            return IngestionResultDTO(
                status="duplicate",
                action_taken=IngestionAction.DUPLICATE.value,
                dataset_name=None,
                parquet_path=None,
                rows_inserted=0,
                message="El archivo fue rechazado porque su Hash MD5 ya existe (Duplicado exacto)."
            )

        # 2. Análisis del Esquema Entrante
        incoming_schema = self.schema_analyzer.extract_schema(source_csv_path)
        
        # 3. Decisión (Ruteo)
        catalog = self.catalog_repo.get_catalog()
        decision = IngestionDecisionDTO(action=IngestionAction.CREATE_NEW, reason="No se encontraron datasets")
        
        for dataset_name, meta in catalog.datasets.items():
            if self._compare_schemas(incoming_schema, meta.schema_definition):
                coercion = self._get_coercion_types(incoming_schema, meta.schema_definition)
                decision = IngestionDecisionDTO(
                    action=IngestionAction.APPEND,
                    dataset_name=dataset_name,
                    types_coercion=coercion if coercion else None,
                    reason=f"Las columnas coinciden exactamente con el dataset '{dataset_name}'."
                )
                break
        
        if decision.action == IngestionAction.CREATE_NEW:
            # Asignamos un nuevo nombre genérico o podríamos extraerlo del archivo
            new_id = len(catalog.datasets) + 1
            decision.dataset_name = f"Dataset_{new_id}"
            decision.reason = "Estructura de columnas única, se requiere un dataset nuevo."

        # 4. Almacenamiento Particionado en Bronce
        # En lugar de un solo bronze.parquet, lo metemos en bronze/Dataset_X/uuid.parquet
        part_id = str(uuid.uuid4())
        target_parquet = Path(bronze_base_dir) / decision.dataset_name / f"part_{part_id}.parquet"
        target_parquet.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            rows = self.schema_analyzer.convert_to_parquet(
                source_csv_path, 
                str(target_parquet),
                types_coercion=decision.types_coercion
            )
        except Exception as e:
            # Falla de Coerción Estricta
            return IngestionResultDTO(
                status="error",
                action_taken=decision.action.value,
                dataset_name=decision.dataset_name,
                parquet_path=None,
                rows_inserted=0,
                message=f"Fallo de coerción estricta o error de lectura: {str(e)}"
            )

        # 5. Actualización del Catálogo
        self.catalog_repo.register_file_hash(file_hash, decision.dataset_name, target_parquet.name)
        
        now_str = datetime.now().isoformat()
        if decision.action == IngestionAction.CREATE_NEW:
            meta = DatasetMetadataDTO(
                name=decision.dataset_name,
                schema_definition=incoming_schema,
                partition_files=[target_parquet.name],
                created_at=now_str,
                updated_at=now_str
            )
            catalog.datasets[decision.dataset_name] = meta
        else:
            meta = catalog.datasets[decision.dataset_name]
            meta.partition_files.append(target_parquet.name)
            meta.updated_at = now_str
            
        self.catalog_repo.save_catalog(catalog)

        return IngestionResultDTO(
            status="success",
            action_taken=decision.action.value,
            dataset_name=decision.dataset_name,
            parquet_path=str(target_parquet),
            rows_inserted=rows,
            message=decision.reason
        )
