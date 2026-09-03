import os
import shutil
import duckdb
from pathlib import Path
import pytest

from src.data_ingestion.domain.models import IngestionAction
from src.data_ingestion.infrastructure.duckdb_schema_analyzer import DuckDBSchemaAnalyzer
from src.data_ingestion.infrastructure.json_catalog_repository import JsonCatalogRepository
from src.data_ingestion.application.upload_dataset_use_case import UploadDatasetUseCase
from src.shared.infrastructure.duckdb_journal_repository import DuckDBJournalRepository

@pytest.fixture
def ingestion_setup(tmp_path):
    # Setup temporal project
    project_id = "test_project"
    storage_path = tmp_path / "data" / "projects" / project_id
    bronze_dir = storage_path / "bronze"
    catalog_path = storage_path / "catalog.json"
    
    # Setup repos and use case
    storage_path.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(storage_path / "duck.db"))
    repo = DuckDBJournalRepository(conn)
    schema_analyzer = DuckDBSchemaAnalyzer(repo.conn)
    catalog_repo = JsonCatalogRepository(str(catalog_path), project_id)
    use_case = UploadDatasetUseCase(catalog_repo, schema_analyzer)
    
    return {
        "use_case": use_case,
        "bronze_dir": bronze_dir,
        "tmp_path": tmp_path,
        "catalog_repo": catalog_repo
    }

def test_upload_new_dataset(ingestion_setup):
    use_case = ingestion_setup["use_case"]
    tmp_path = ingestion_setup["tmp_path"]
    
    # Crear CSV falso
    csv_file = tmp_path / "ventas1.csv"
    csv_file.write_text("fecha,total\n2023-01-01,100.5\n")
    
    result = use_case.execute(str(csv_file), str(ingestion_setup["bronze_dir"]))
    
    assert result.action_taken == IngestionAction.CREATE_NEW.value
    assert result.dataset_name == "Dataset_1"
    assert result.rows_inserted == 1
    assert Path(result.parquet_path).exists()

def test_upload_duplicate_rejected(ingestion_setup):
    use_case = ingestion_setup["use_case"]
    tmp_path = ingestion_setup["tmp_path"]
    
    csv_file = tmp_path / "ventas1.csv"
    csv_file.write_text("fecha,total\n2023-01-01,100.5\n")
    
    # Primera subida
    use_case.execute(str(csv_file), str(ingestion_setup["bronze_dir"]))
    
    # Segunda subida exacta
    result2 = use_case.execute(str(csv_file), str(ingestion_setup["bronze_dir"]))
    
    assert result2.action_taken == IngestionAction.DUPLICATE.value
    assert result2.status == "duplicate"
    assert result2.rows_inserted == 0

def test_upload_append_with_same_schema(ingestion_setup):
    use_case = ingestion_setup["use_case"]
    tmp_path = ingestion_setup["tmp_path"]
    
    # CSV 1
    csv1 = tmp_path / "ventas1.csv"
    csv1.write_text("fecha,total\n2023-01-01,100.5\n")
    res1 = use_case.execute(str(csv1), str(ingestion_setup["bronze_dir"]))
    
    # CSV 2 con misma estructura pero diferentes datos
    csv2 = tmp_path / "ventas2.csv"
    csv2.write_text("fecha,total\n2023-02-01,200.0\n")
    res2 = use_case.execute(str(csv2), str(ingestion_setup["bronze_dir"]))
    
    assert res2.action_taken == IngestionAction.APPEND.value
    assert res2.dataset_name == res1.dataset_name  # Dataset_1
    assert res2.rows_inserted == 1
    
    # Verificar el catálogo
    cat = ingestion_setup["catalog_repo"].get_catalog()
    assert len(cat.datasets["Dataset_1"].partition_files) == 2

def test_upload_append_with_coercion_and_failure(ingestion_setup):
    use_case = ingestion_setup["use_case"]
    tmp_path = ingestion_setup["tmp_path"]
    
    # CSV 1 (Esquema maestro: total es DOUBLE)
    csv1 = tmp_path / "ventas1.csv"
    csv1.write_text("fecha,total\n2023-01-01,100.5\n")
    use_case.execute(str(csv1), str(ingestion_setup["bronze_dir"]))
    
    # CSV 2 (Mismas columnas pero la columna total trae texto, intentará coerción)
    csv2 = tmp_path / "ventas2.csv"
    csv2.write_text("fecha,total\n2023-02-01,Basura\n")
    res2 = use_case.execute(str(csv2), str(ingestion_setup["bronze_dir"]))
    
    # En la Capa Bronce se preservan los datos crudos como VARCHAR sin perder filas
    assert res2.status == "success"
    assert res2.rows_inserted == 1

