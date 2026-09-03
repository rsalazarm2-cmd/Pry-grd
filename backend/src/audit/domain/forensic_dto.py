"""DTOs Pydantic para el Dominio de Auditoría Forense y Detección de Riesgos.

Cubre Casos de Uso CU-16 (SoD & Aprobaciones Exprés), CU-17 (Trampas Forenses),
CU-18 (Análisis Cut-off) y CU-19 (Financial Integrity Risk Score).
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class SodViolationDTO(BaseModel):
    """CU-16: Violación de Segregación de Funciones o Aprobación Exprés."""

    folio_asiento: str
    usuario_registrador: str
    usuario_aprobador: str
    fecha_registro: str
    monto_total: float = 0.0
    tipo_violacion: str = "MAKER_EQUAL_CHECKER"  # MAKER_EQUAL_CHECKER o RAPID_APPROVAL
    diferencia_segundos: Optional[float] = None
    nivel_riesgo: str = "ALTO"


class ForensicTrapAlertDTO(BaseModel):
    """CU-17: Alerta de Trampa Forense (Medianoche, Monto Redondo, Fin de Semana)."""

    folio_asiento: str
    tipo_trampa: str  # MIDNIGHT_STAMP, ROUND_AMOUNT, WEEKEND_REGISTRATION
    descripcion_trampa: str
    fecha_registro: str
    monto: float = 0.0
    nivel_riesgo: str = "MEDIO"


class CutoffAnomalyDTO(BaseModel):
    """CU-18: Anomalía de Corte Temporal / Backdating."""

    folio_asiento: str
    periodo_contable: str
    fecha_contabilizacion: str
    fecha_registro: str
    diferencia_dias: int = 0
    descripcion: str
    nivel_riesgo: str = "ALTO"


class IntegrityRiskScoreDTO(BaseModel):
    """CU-19: Matriz de Integridad Financiera y Score de Riesgo (0-100)."""

    total_asientos_analizados: int = 0
    financial_integrity_score: float = 100.0  # 100 = Cero Riesgo
    nivel_riesgo_global: str = "BAJO"  # BAJO, MEDIO, ALTO, CRITICO
    sod_violations_count: int = 0
    forensic_traps_count: int = 0
    cutoff_anomalies_count: int = 0
    imbalanced_entries_count: int = 0


class ForensicAuditMatrixDTO(BaseModel):
    """Consolidado integral de la auditoría forense."""

    score: IntegrityRiskScoreDTO = Field(default_factory=IntegrityRiskScoreDTO)
    sod_violations: List[SodViolationDTO] = Field(default_factory=list)
    forensic_traps: List[ForensicTrapAlertDTO] = Field(default_factory=list)
    cutoff_anomalies: List[CutoffAnomalyDTO] = Field(default_factory=list)
