import os
from typing import List, Optional
from ninja import Router, Query
from ninja.errors import HttpError
from audit_system.backend.infrastructure.repositories import DuckDBAuditRepository
from audit_system.backend.application.use_cases import ValidarIntegridadAsientosUseCase
from audit_system.backend.domain.entities import (
    AlertaDescuadreDTO, SegregacionFuncionesDTO, InformeIntegridadAuditoriaDTO,
)
from src.audit.application.run_forensic_audit_use_case import RunForensicAuditUseCase
from src.audit.domain.forensic_dto import (
    ForensicAuditMatrixDTO, ForensicTrapAlertDTO, CutoffAnomalyDTO,
)
from src.audit.infrastructure.forensic_audit_engine import ForensicAuditEngine
from src.audit.domain.benford_dto import BenfordAnalysisResultDTO
from src.audit.infrastructure.benford_analyzer import BenfordAnalyzer
from src.shared.api.dependencies import resolve_project_paths, get_repository

router = Router(tags=["Auditoría Forense Contable"])

def _get_use_case() -> ValidarIntegridadAsientosUseCase:
    return ValidarIntegridadAsientosUseCase(DuckDBAuditRepository())

def _get_valid_parquet_path(parquet_path: Optional[str], project_id: Optional[str]) -> str:
    paths = resolve_project_paths(project_id)
    if parquet_path and os.path.exists(parquet_path):
        return parquet_path
    if paths["silver"].exists():
        return str(paths["silver"])
    if paths["bronze"].exists():
        return str(paths["bronze"])
    raise HttpError(404, "No se encontró archivo Parquet para analizar.")

@router.get("/imbalances", response=List[AlertaDescuadreDTO])
def get_journal_imbalances(request, parquet_path: Optional[str] = Query(None), project_id: Optional[str] = Query(None), limite: int = Query(100)):
    target_path = _get_valid_parquet_path(parquet_path, project_id)
    return _get_use_case().ejecutar_validacion_descuadres(target_path, limite)

@router.get("/sod-violations", response=List[SegregacionFuncionesDTO])
def get_sod_violations(request, parquet_path: Optional[str] = Query(None), project_id: Optional[str] = Query(None), limite: int = Query(100)):
    target_path = _get_valid_parquet_path(parquet_path, project_id)
    return _get_use_case().ejecutar_validacion_sod(target_path, limite)

@router.get("/report", response=InformeIntegridadAuditoriaDTO)
def get_audit_report(request, parquet_path: Optional[str] = Query(None), project_id: Optional[str] = Query(None)):
    target_path = _get_valid_parquet_path(parquet_path, project_id)
    return _get_use_case().generar_informe_auditoria(target_path)

@router.get("/forensic-matrix", response=ForensicAuditMatrixDTO)
def get_forensic_matrix(request, parquet_path: Optional[str] = Query(None), project_id: Optional[str] = Query(None)):
    """CU-16 a CU-19: Matriz consolidada de auditoría forense y Risk Score."""
    target_path = _get_valid_parquet_path(parquet_path, project_id)
    return RunForensicAuditUseCase().execute(target_path)

@router.get("/traps", response=List[ForensicTrapAlertDTO])
def get_forensic_traps(request, parquet_path: Optional[str] = Query(None), project_id: Optional[str] = Query(None)):
    """CU-17: Trampas forenses (medianoche, montos redondos, fin de semana)."""
    target_path = _get_valid_parquet_path(parquet_path, project_id)
    engine = ForensicAuditEngine(get_repository().conn)
    return engine.analyze_forensic_traps(target_path)

@router.get("/cutoff-anomalies", response=List[CutoffAnomalyDTO])
def get_cutoff_anomalies(request, parquet_path: Optional[str] = Query(None), project_id: Optional[str] = Query(None)):
    """CU-18: Anomalías de corte temporal y backdating."""
    target_path = _get_valid_parquet_path(parquet_path, project_id)
    engine = ForensicAuditEngine(get_repository().conn)
    return engine.analyze_cutoff_anomalies(target_path)

@router.get("/benford", response=BenfordAnalysisResultDTO)
def get_benford_analysis(request, parquet_path: Optional[str] = Query(None), project_id: Optional[str] = Query(None), column_name: str = "CARGO_MONEDA_FUNCIONAL"):
    """Evaluación de la Ley de Benford (1er y 2º dígito) sobre montos."""
    target_path = _get_valid_parquet_path(parquet_path, project_id)
    repo = get_repository()
    view_name = "view_benford_target"
    repo.conn.execute(f"CREATE OR REPLACE VIEW {view_name} AS SELECT * FROM read_parquet('{target_path}')")
    return BenfordAnalyzer(repo.conn).analyze_column(view_name, column_name=column_name)
