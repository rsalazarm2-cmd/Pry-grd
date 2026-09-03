"""DTOs Pydantic para el Motor de Scoring Consolidado de Riesgo en Capa Oro (0-100).

Consolida los 5 vectores forenses y las 9 pruebas analíticas en una matriz
unificada de puntuación por asiento contable y por usuario/entidad.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class JournalRiskScoreDTO(BaseModel):
    """Puntuación de riesgo consolidada para un asiento contable individual."""

    folio_asiento: str = Field(description="Identificador del asiento.")
    score_global: float = Field(description="Score de riesgo ponderado (0.0 a 100.0).")
    nivel_riesgo: str = Field(description="Clasificación: BAJO, MEDIO, ALTO, CRITICO.")
    usuario_registrador: str = Field(default="ANON")
    monto_total: float = Field(default=0.0)
    factores_riesgo: List[str] = Field(default_factory=list, description="Lista de reglas gatilladas.")
    detalles_ponderacion: dict = Field(default_factory=dict, description="Desglose numérico de puntos.")


class UserRiskDatamartItemDTO(BaseModel):
    """Agregación de riesgo por usuario en Datamart Ejecutivo Oro."""

    usuario: str = Field(description="Nombre o ID del usuario registrador.")
    total_asientos: int = Field(default=0)
    asientos_alto_riesgo: int = Field(default=0)
    monto_total_registrado: float = Field(default=0.0)
    score_promedio_usuario: float = Field(default=0.0)
    casos_sod_count: int = Field(default=0)
    casos_fraccionamiento_count: int = Field(default=0)


class GoldExecutiveRiskDatamartDTO(BaseModel):
    """Datamart Consolidado Ejecutivo de la Capa Oro."""

    total_asientos_analizados: int = 0
    score_promedio_general: float = 0.0
    total_asientos_criticos: int = 0
    total_monto_en_riesgo: float = 0.0
    top_asientos_criticos: List[JournalRiskScoreDTO] = Field(default_factory=list)
    top_usuarios_riesgosos: List[UserRiskDatamartItemDTO] = Field(default_factory=list)
