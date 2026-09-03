import logging
from typing import Dict, Any, Optional
from django.http import HttpResponse

from ninja import Router, Query
from ninja.errors import HttpError

from src.gold.application.query_gold_account_balances_use_case import QueryGoldAccountBalancesUseCase
from src.gold.application.query_gold_balances_use_case import QueryGoldBalancesUseCase
from src.gold.application.generate_gold_models_use_case import GenerateGoldModelsUseCase
from src.gold.domain.gold_models_dto import GoldDatamartResultDTO, GoldIntegritySummaryDTO
from src.gold.domain.risk_scoring_dto import GoldExecutiveRiskDatamartDTO
from src.gold.infrastructure.gold_risk_scoring_engine import GoldRiskScoringEngine
from src.gold.infrastructure.gold_datamart_engine import GoldDatamartEngine
from src.gold.infrastructure.excel_export_service import ExcelExportService
from src.shared.domain.journal_entry import TabularResultDTO
from src.shared.api.dependencies import resolve_project_paths, get_repository

logger = logging.getLogger(__name__)
router = Router()


@router.post("/generate", response=GoldDatamartResultDTO, tags=["Gold Layer"])
def generate_gold_datamarts(request, project_id: Optional[str] = Query(None)):
    """CU-11 / CU-12 / CU-13: Genera datamarts Oro y calcula integridad."""
    paths = resolve_project_paths(project_id)
    if not paths["silver"].exists():
        raise HttpError(400, "No existe el archivo Parquet Plata para este proyecto. Procesa la Capa Plata primero.")
    return GenerateGoldModelsUseCase().execute(str(paths["silver"]), str(paths["gold_dir"]))


@router.get("/integrity-summary", response=GoldIntegritySummaryDTO, tags=["Gold Layer"])
def get_integrity_summary(request, project_id: Optional[str] = Query(None)):
    """CU-13: Resumen global de cuadre financiero."""
    paths = resolve_project_paths(project_id)
    target = paths["silver"] if paths["silver"].exists() else paths["bronze"]
    if not target.exists():
        return GoldIntegritySummaryDTO()
    engine = GoldDatamartEngine(get_repository().conn)
    return engine.compute_integrity_summary(target)


@router.get("/export-excel", tags=["Gold Layer"])
def export_excel_report(request, project_id: Optional[str] = Query(None)):
    """CU-14: Descarga del informe financiero ejecutivo en Excel (.xlsx)."""
    paths = resolve_project_paths(project_id)
    target = paths["silver"] if paths["silver"].exists() else paths["bronze"]
    if not target.exists():
        raise HttpError(400, "No hay datos procesados para exportar.")

    exporter = ExcelExportService(get_repository().conn)
    excel_bytes = exporter.export_gold_report(target, paths["gold_dir"])

    filename = f"Informe_Financiero_{paths['project'].name}.xlsx"
    response = HttpResponse(
        excel_bytes,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@router.get("/balances", response=TabularResultDTO, tags=["Gold Layer"])
def get_gold_balances(request, project_id: Optional[str] = Query(None), search: Optional[str] = None, column_name: Optional[str] = None, filters_json: Optional[str] = None):
    paths = resolve_project_paths(project_id)
    return QueryGoldBalancesUseCase(get_repository()).execute(str(paths["gold_ledger"]), search, column_name, filters_json)


@router.get("/account-balances", response=TabularResultDTO, tags=["Gold Layer"])
def get_gold_account_balances(request, project_id: Optional[str] = Query(None), search: Optional[str] = None, column_name: Optional[str] = None, filters_json: Optional[str] = None):
    paths = resolve_project_paths(project_id)
    return QueryGoldAccountBalancesUseCase(get_repository()).execute(str(paths["gold_account"]), search, column_name, filters_json)


@router.get("/distinct-values/ledger/{column_name}", response=list[Dict[str, Any]], tags=["Gold Layer"])
def get_ledger_distinct_values(request, column_name: str, project_id: Optional[str] = Query(None)):
    paths = resolve_project_paths(project_id)
    return get_repository().get_column_distinct_values(str(paths["gold_ledger"]), column_name)


@router.get("/distinct-values/account/{column_name}", response=list[Dict[str, Any]], tags=["Gold Layer"])
def get_account_distinct_values(request, column_name: str, project_id: Optional[str] = Query(None)):
    paths = resolve_project_paths(project_id)
    return get_repository().get_column_distinct_values(str(paths["gold_account"]), column_name)


@router.get("/risk-datamart", response=GoldExecutiveRiskDatamartDTO, tags=["Gold Layer - Executive Risk"])
def get_gold_risk_datamart(request, project_id: Optional[str] = Query(None)):
    """Data Mart Ejecutivo de Scoring Consolidado de Riesgo (0-100) en Capa Oro."""
    paths = resolve_project_paths(project_id)
    target = paths["silver"] if paths["silver"].exists() else paths["bronze"]
    if not target.exists():
        return GoldExecutiveRiskDatamartDTO()
    repo = get_repository()
    view_name = "view_gold_risk_target"
    repo.conn.execute(f"CREATE OR REPLACE VIEW {view_name} AS SELECT * FROM read_parquet('{target}')")
    return GoldRiskScoringEngine(repo.conn).generate_executive_datamart(view_name)
