import logging
from pathlib import Path
from typing import Dict, Any, Optional
from uuid import uuid4

from django.conf import settings
from ninja import Router, Query, File, UploadedFile
from ninja.errors import HttpError

from src.bronze.application.ingest_bronze_use_case import IngestBronzeDataUseCase
from src.bronze.application.profile_dataset_use_case import ProfileDatasetUseCase
from src.bronze.application.query_bronze_records_use_case import QueryBronzeRecordsUseCase
from src.data_ingestion.infrastructure.duckdb_schema_analyzer import DuckDBSchemaAnalyzer
from src.data_ingestion.infrastructure.json_catalog_repository import JsonCatalogRepository
from src.data_ingestion.application.upload_dataset_use_case import UploadDatasetUseCase
from src.data_ingestion.domain.models import IngestionResultDTO
from src.shared.domain.journal_entry import (
    BronzeIngestionResultDTO,
    ColumnProfileDTO,
    DatasetProfileDTO,
    TabularResultDTO,
)
from src.shared.api.dependencies import resolve_project_paths, get_repository, get_project_repository


logger = logging.getLogger(__name__)

router = Router()

ALLOWED_UPLOAD_EXTENSIONS = {".csv", ".txt", ".tsv"}
MAX_UPLOAD_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB

def _validate_upload(file: UploadedFile) -> str:
    ext = Path(file.name).suffix.lower()
    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HttpError(400, f"Extensión '{ext}' no permitida. Solo se aceptan: {', '.join(ALLOWED_UPLOAD_EXTENSIONS)}")

    if file.size and file.size > MAX_UPLOAD_SIZE_BYTES:
        raise HttpError(413, f"El archivo excede el límite de {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB.")

    return f"temp_{uuid4().hex}{ext}"

@router.post("/upload-ingest", response=IngestionResultDTO, tags=["Bronze Layer"])
def upload_ingest_bronze(request, file: UploadedFile = File(...), project_id: Optional[str] = Query(None)):
    safe_name = _validate_upload(file)

    p_repo = get_project_repository()
    if project_id:
        proj_slug = p_repo._slugify(project_id)
        project = p_repo.get_project(proj_slug)
        if not project:
            from src.project.domain.project import CreateProjectDTO
            project = p_repo.create_project(CreateProjectDTO(name=project_id, description="Proyecto cargado por el auditor"))
    else:
        project = p_repo.get_or_default("proyecto-principal")

    storage_path = Path(project.storage_path)
    temp_csv_path = storage_path / "raw" / safe_name
    temp_csv_path.parent.mkdir(parents=True, exist_ok=True)

    with open(temp_csv_path, "wb") as f:
        for chunk in file.chunks():
            f.write(chunk)

    bronze_dir = storage_path / "bronze"
    bronze_dir.mkdir(parents=True, exist_ok=True)
    target_parquet = bronze_dir / "bronze.parquet"

    repo = get_repository()
    schema_analyzer = DuckDBSchemaAnalyzer(repo.conn)
    rows_inserted = schema_analyzer.convert_to_parquet(str(temp_csv_path), str(target_parquet))

    if temp_csv_path.exists():
        temp_csv_path.unlink()

    return IngestionResultDTO(
        status="success",
        action_taken="CREATE_NEW",
        dataset_name=project.name,
        parquet_path=str(target_parquet),
        rows_inserted=rows_inserted,
        message=f"Dataset subido exitosamente al proyecto '{project.name}'."
    )



@router.post("/ingest", response=BronzeIngestionResultDTO, tags=["Bronze Layer"])
def ingest_bronze(request, project_id: Optional[str] = Query(None)):
    paths = resolve_project_paths(project_id)
    source_csv = Path(paths["project"].storage_path) / "raw" / "datos.csv"
    if not source_csv.exists():
        source_csv = settings.PROJECT_ROOT / "datos.csv"

    repo = get_repository()
    result = IngestBronzeDataUseCase(repo).execute(str(source_csv), str(paths["bronze"]))
    return result


@router.get("/records", response=TabularResultDTO, tags=["Bronze Layer"])
def get_bronze_records(request, project_id: Optional[str] = Query(None), limit: int = 50, search: Optional[str] = None, column_name: Optional[str] = None, filters_json: Optional[str] = None):
    paths = resolve_project_paths(project_id)
    return QueryBronzeRecordsUseCase(get_repository()).execute(str(paths["bronze"]), limit, search, column_name, filters_json)


@router.get("/profile", response=DatasetProfileDTO, tags=["Bronze Layer"])
def profile_bronze(request, project_id: Optional[str] = Query(None)):
    paths = resolve_project_paths(project_id)
    return ProfileDatasetUseCase(get_repository()).execute(str(paths["bronze"]))

from src.shared.domain.journal_entry import BronzeToSilverRulesDTO
from src.bronze.application.suggest_mapping_use_case import SuggestMappingUseCase

@router.get("/suggest-mapping", response=BronzeToSilverRulesDTO, tags=["Bronze Layer"])
def suggest_mapping(request, project_id: Optional[str] = Query(None), target_lang: str = Query("es"), force: bool = Query(False)):
    paths = resolve_project_paths(project_id)
    return SuggestMappingUseCase(get_repository()).execute(str(paths["bronze"]), target_lang=target_lang, force=force)

from src.shared.domain.journal_entry import SilverTargetEntityDTO
from src.ai_translator.application.suggest_multitable_schema_use_case import SuggestMultitableSchemaUseCase

@router.get("/suggest-multitable-model", response=list[SilverTargetEntityDTO], tags=["Bronze Layer"])
def suggest_multitable_model(request, project_id: Optional[str] = Query(None)):
    paths = resolve_project_paths(project_id)
    return SuggestMultitableSchemaUseCase(get_repository()).execute(str(paths["bronze"]))






@router.get("/column-detail/{column_name}", response=ColumnProfileDTO, tags=["Bronze Layer"])
def get_column_detail(request, column_name: str, project_id: Optional[str] = Query(None)):
    paths = resolve_project_paths(project_id)
    profile = ProfileDatasetUseCase(get_repository()).execute(str(paths["bronze"]))

    for col in profile.columns:
        if col.column_name.lower() == column_name.lower():
            return col

    raise HttpError(404, f"Columna '{column_name}' no encontrada.")

@router.get("/distinct-values/{column_name}", response=list[Dict[str, Any]], tags=["Bronze Layer"])
def get_column_distinct_values(request, column_name: str, project_id: Optional[str] = Query(None)):
    paths = resolve_project_paths(project_id)
    return get_repository().get_column_distinct_values(str(paths["bronze"]), column_name)

from src.shared.domain.journal_entry import SystemConfigOptionsDTO, ConfigOptionDTO

@router.get("/config-options", response=SystemConfigOptionsDTO, tags=["Bronze Layer"])
def get_config_options(request):
    return SystemConfigOptionsDTO(
        available_data_types=[
            ConfigOptionDTO(id="VARCHAR", label="Texto (VARCHAR)"),
            ConfigOptionDTO(id="INTEGER", label="INTEGER (Entero Simple)"),
            ConfigOptionDTO(id="BIGINT", label="BIGINT (Entero Grande)"),
            ConfigOptionDTO(id="DOUBLE", label="DOUBLE (Decimales)"),
            ConfigOptionDTO(id="DATE", label="DATE (Fecha Simple)"),
            ConfigOptionDTO(id="TIMESTAMP", label="TIMESTAMP (Fecha y Hora)"),
        ],
        null_imputation_strategies=[
            ConfigOptionDTO(id="DEFAULT", label="Dejar Nulo (Por Defecto)"),
            ConfigOptionDTO(id="ZERO", label="Rellenar con 0 (Numérico)"),
            ConfigOptionDTO(id="EMPTY", label="Cadena Vacía '' (Texto)"),
            ConfigOptionDTO(id="UNKNOWN", label="Rellenar con 'DESCONOCIDO' (Texto)"),
            ConfigOptionDTO(id="MEAN", label="Imputar con Media Aritmética"),
        ],
        duplicate_action_modes=[
            ConfigOptionDTO(id="FLAG_QUARANTINE", label="🏷️ Modo 1: Marcar en Cuarentena"),
            ConfigOptionDTO(id="PREFIX_DUP", label="🏷️ Modo 2: Renombrar Asientos con Prefijo DUP_"),
            ConfigOptionDTO(id="PURGE_DELETE", label="🗑️ Modo 3: Purga Controlada (Eliminar en Plata)"),
        ]
    )
