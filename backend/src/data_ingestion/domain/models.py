from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class IngestionAction(str, Enum):
    APPEND = "APPEND"
    CREATE_NEW = "CREATE_NEW"
    DUPLICATE = "DUPLICATE"

class ColumnSchemaDTO(BaseModel):
    name: str
    data_type: str

class DatasetMetadataDTO(BaseModel):
    name: str
    schema_definition: List[ColumnSchemaDTO]
    partition_files: List[str] = Field(default_factory=list)
    created_at: str
    updated_at: str

class CatalogDTO(BaseModel):
    project_id: str
    datasets: Dict[str, DatasetMetadataDTO] = Field(default_factory=dict)

class IngestionDecisionDTO(BaseModel):
    action: IngestionAction
    dataset_name: Optional[str] = None
    target_parquet_path: Optional[str] = None
    types_coercion: Optional[Dict[str, str]] = None
    reason: str

class IngestionResultDTO(BaseModel):
    status: str
    action_taken: str
    dataset_name: Optional[str]
    parquet_path: Optional[str]
    rows_inserted: int
    message: str
