import logging
from typing import Optional
from pathlib import Path

from django.conf import settings
from ninja import Router, Query

from src.shared.application.execute_pipeline_use_case import ExecutePipelineUseCase, PipelineExecutionSummaryDTO
from src.shared.domain.journal_entry import BronzeToSilverRulesDTO
from src.shared.api.dependencies import resolve_project_paths, get_repository

logger = logging.getLogger(__name__)

router = Router()

@router.post("/execute", response=PipelineExecutionSummaryDTO, tags=["Medallion Pipeline"])
def execute_pipeline(request, bronze_rules: BronzeToSilverRulesDTO = None, project_id: Optional[str] = Query(None)):
    paths = resolve_project_paths(project_id)
    source_csv = Path(paths["project"].storage_path) / "raw" / "datos.csv"
    if not source_csv.exists():
        # Fallback for testing
        source_csv = settings.PROJECT_ROOT / "datos.csv"

    repo = get_repository()
    result = ExecutePipelineUseCase(repo).execute(
        str(source_csv), str(paths["bronze"]), str(paths["silver"]), bronze_rules
    )
    return result
