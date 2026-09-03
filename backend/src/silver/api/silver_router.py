import logging
from typing import Dict, Any, Optional

from ninja import Router, Query
from ninja.errors import HttpError

from src.silver.application.query_silver_records_use_case import QuerySilverRecordsUseCase
from src.silver.application.transform_silver_use_case import TransformSilverDataUseCase
from src.silver.application.date_expression_use_cases import (
    ComputeDateRedundancyUseCase, ComputeDateDeltaUseCase, ComputeWeekdayDistributionUseCase,
    PreviewAmountSplitUseCase, ListDateColumnsUseCase, ListNumericColumnsUseCase,
)
from src.silver.application.rule_evaluator_use_cases import EvaluateConditionalRuleUseCase
from src.silver.domain.atomicity import AtomicitySuggestionDTO
from src.silver.domain.date_expression_ast import (
    DatePairDTO, DateRedundancyResultDTO, DateDeltaResultDTO, WeekdayResultDTO, AmountSplitResultDTO,
)
from src.silver.domain.rule_expression_dto import ConditionalRuleDTO, RuleEvaluationResultDTO
from src.silver.domain.forensic_vector_dto import ForensicAuditSummaryDTO, ForensicVectorRecordDTO
from src.silver.application.forensic_vector_use_cases import ForensicVectorUseCases
from src.silver.domain.lineage_dto import LineageMatrixDTO
from src.silver.infrastructure.silver_lineage_service import SilverLineageService
from src.silver.infrastructure.atomicity_service import AtomicityDuckDBService
from src.bronze.application.profile_dataset_use_case import ProfileDatasetUseCase
from src.bronze.infrastructure.mapping_rules_persistence_service import MappingRulesPersistenceService
from src.shared.domain.journal_entry import (
    DatasetProfileDTO, SilverTransformationResultDTO, TabularResultDTO,
    BronzeToSilverRulesDTO, TransformationRulesDTO,
)
from src.shared.api.dependencies import resolve_project_paths, get_repository, get_project_repository

logger = logging.getLogger(__name__)
router = Router()


@router.get("/profile", response=DatasetProfileDTO, tags=["Silver Layer"])
def profile_silver(request, project_id: Optional[str] = Query(None)):
    paths = resolve_project_paths(project_id)
    if not paths["silver"].exists():
        return ProfileDatasetUseCase(get_repository()).execute(str(paths["bronze"]))
    return ProfileDatasetUseCase(get_repository()).execute(str(paths["silver"]))


@router.get("/saved-rules", response=Optional[BronzeToSilverRulesDTO], tags=["Silver Layer"])
def get_saved_rules(request, project_id: Optional[str] = Query(None)):
    paths = resolve_project_paths(project_id)
    return MappingRulesPersistenceService.load_saved_rules(paths["bronze"]) if paths["bronze"].exists() else None


@router.get("/lineage", response=LineageMatrixDTO, tags=["Silver Layer"])
def get_lineage_matrix(request, project_id: Optional[str] = Query(None)):
    paths = resolve_project_paths(project_id)
    return SilverLineageService(get_repository().conn).get_lineage_matrix(paths["bronze"], paths["silver"], project_id=paths["project"].id)


@router.post("/transform", response=SilverTransformationResultDTO, tags=["Silver Layer"])
def transform_silver(request, rules: BronzeToSilverRulesDTO = None, project_id: Optional[str] = Query(None)):
    paths = resolve_project_paths(project_id)
    if not paths["bronze"].exists():
        raise HttpError(400, f"No existe el archivo Parquet Bronce para el proyecto '{paths['project'].name}'.")

    try:
        repo = get_repository()
        result = TransformSilverDataUseCase(repo).execute(str(paths["bronze"]), str(paths["silver"]), rules)
        if rules:
            MappingRulesPersistenceService.save_rules(paths["bronze"], rules)
            p_repo = get_project_repository()
            existing_recipe = p_repo.get_recipe(paths["project"].id)
            if existing_recipe:
                merged_dict = existing_recipe.model_dump()
                merged_dict.update(rules.model_dump(exclude_unset=True))
                full_rules = TransformationRulesDTO(**merged_dict)
            else:
                full_rules = TransformationRulesDTO(**rules.model_dump())
            p_repo.save_recipe(paths["project"].id, full_rules)
        return result
    except Exception as e:
        logger.error("Error en transform_silver: %s", e, exc_info=True)
        raise HttpError(400, f"Error al procesar la Capa Plata: {str(e)}")


@router.get("/atomicity-suggestions", response=list[AtomicitySuggestionDTO], tags=["Silver Layer"])
def get_atomicity_suggestions(request, project_id: Optional[str] = Query(None)):
    paths = resolve_project_paths(project_id)
    if not paths["bronze"].exists():
        return []
    try:
        return AtomicityDuckDBService(get_repository().conn).get_atomicity_suggestions(str(paths["bronze"]))
    except Exception as e:
        logger.error("Error obteniendo sugerencias de atomización: %s", e, exc_info=True)
        return []


@router.get("/records", response=TabularResultDTO, tags=["Silver Layer"])
def get_silver_records(
    request, project_id: Optional[str] = Query(None), quality_status: Optional[str] = None,
    limit: int = 50, search: Optional[str] = None, column_name: Optional[str] = None,
    filters_json: Optional[str] = None, view_mode: Optional[str] = "ALL",
):
    paths = resolve_project_paths(project_id)
    return QuerySilverRecordsUseCase(get_repository()).execute(
        str(paths["silver"]), quality_status, limit, search, column_name, filters_json, view_mode
    )


@router.get("/distinct-values/{column_name}", response=list[Dict[str, Any]], tags=["Silver Layer"])
def get_column_distinct_values(request, column_name: str, project_id: Optional[str] = Query(None)):
    paths = resolve_project_paths(project_id)
    return get_repository().get_column_distinct_values(str(paths["silver"]), column_name)


def _resolve_active_parquet(project_id: Optional[str]) -> str:
    paths = resolve_project_paths(project_id)
    target = paths["silver"] if paths["silver"].exists() else paths["bronze"]
    if not target.exists():
        raise HttpError(400, "No existe Parquet Bronce ni Plata para este proyecto.")
    return str(target)


@router.get("/date-columns", response=list[str], tags=["Silver Layer - Date Engine"])
def list_date_columns(request, project_id: Optional[str] = Query(None)):
    return ListDateColumnsUseCase().execute(_resolve_active_parquet(project_id))


@router.post("/date-redundancy", response=DateRedundancyResultDTO, tags=["Silver Layer - Date Engine"])
def compute_date_redundancy(request, pair: DatePairDTO, project_id: Optional[str] = Query(None)):
    return ComputeDateRedundancyUseCase().execute(_resolve_active_parquet(project_id), pair.date_column_a, pair.date_column_b)


@router.post("/date-delta", response=DateDeltaResultDTO, tags=["Silver Layer - Date Engine"])
def compute_date_delta(request, pair: DatePairDTO, project_id: Optional[str] = Query(None)):
    return ComputeDateDeltaUseCase().execute(_resolve_active_parquet(project_id), pair.date_column_a, pair.date_column_b)


@router.get("/weekday-distribution", response=WeekdayResultDTO, tags=["Silver Layer - Date Engine"])
def compute_weekday_distribution(request, date_column: str, project_id: Optional[str] = Query(None)):
    return ComputeWeekdayDistributionUseCase().execute(_resolve_active_parquet(project_id), date_column)


@router.get("/numeric-columns", response=list[str], tags=["Silver Layer - Amount Engine"])
def list_numeric_columns(request, project_id: Optional[str] = Query(None)):
    return ListNumericColumnsUseCase().execute(_resolve_active_parquet(project_id))


@router.post("/amount-split-preview", response=AmountSplitResultDTO, tags=["Silver Layer - Amount Engine"])
def preview_amount_split(request, source_column: str, project_id: Optional[str] = Query(None)):
    return PreviewAmountSplitUseCase().execute(_resolve_active_parquet(project_id), source_column)


@router.post("/evaluate-rule", response=RuleEvaluationResultDTO, tags=["Silver Layer - Rule Evaluator"])
def evaluate_conditional_rule(request, rule: ConditionalRuleDTO, project_id: Optional[str] = Query(None)):
    return EvaluateConditionalRuleUseCase().execute(_resolve_active_parquet(project_id), rule)

from src.shared.domain.journal_entry import SilverTargetEntityDTO
from src.ai_translator.application.suggest_multitable_schema_use_case import SuggestMultitableSchemaUseCase

@router.get("/suggest-multitable-model", response=list[SilverTargetEntityDTO], tags=["Silver Layer"])
def suggest_multitable_model(request, project_id: Optional[str] = Query(None)):
    target_parquet = _resolve_active_parquet(project_id)
    return SuggestMultitableSchemaUseCase(get_repository()).execute(target_parquet)


@router.get("/forensic-summary", response=ForensicAuditSummaryDTO, tags=["Silver Layer - Forensic Vector"])
def get_forensic_summary(request, project_id: Optional[str] = Query(None)):
    target_parquet = _resolve_active_parquet(project_id)
    repo = get_repository()
    view_name = "view_forensic_parquet"
    repo.conn.execute(f"CREATE OR REPLACE VIEW {view_name} AS SELECT * FROM read_parquet('{target_parquet}')")
    return ForensicVectorUseCases(repo.conn).run_forensic_summary(view_name)


@router.get("/forensic-high-risk", response=list[ForensicVectorRecordDTO], tags=["Silver Layer - Forensic Vector"])
def get_forensic_high_risk(request, project_id: Optional[str] = Query(None), limit: int = 50):
    target_parquet = _resolve_active_parquet(project_id)
    repo = get_repository()
    view_name = "view_forensic_parquet"
    repo.conn.execute(f"CREATE OR REPLACE VIEW {view_name} AS SELECT * FROM read_parquet('{target_parquet}')")
    return ForensicVectorUseCases(repo.conn).fetch_high_risk_records(view_name, limit=limit)

