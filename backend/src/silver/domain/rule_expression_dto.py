"""DTOs Pydantic para el Evaluador de Reglas Condicionales No-Code con soporte AST (CU-09).

Soporta condiciones atómicas, sub-grupos anidados con paréntesis ((A AND B) OR C)
y previsualizaciones sobre Parquet (CU-10).
"""

from typing import Any, List, Optional
from pydantic import BaseModel, Field


class RuleConditionDTO(BaseModel):
    """Condición atómica de regla (ej. MONTO > 100000)."""

    column_name: str = Field(description="Columna evaluada.")
    operator: str = Field(
        default="GT",
        description="Operador: GT, GTE, LT, LTE, EQ, NEQ, IN, IS_NULL, NOT_NULL, IS_WEEKEND, WEEKDAY_EQ",
    )
    value: Any = Field(default=None, description="Valor o lista de valores a comparar.")


class RuleGroupDTO(BaseModel):
    """Grupo de condiciones anidado con paréntesis para expresiones complejas AST."""

    logical_operator: str = Field(default="AND", description="Operador lógico del grupo: AND u OR.")
    conditions: List[RuleConditionDTO] = Field(default_factory=list, description="Condiciones atómicas en este nivel.")
    sub_groups: List["RuleGroupDTO"] = Field(default_factory=list, description="Sub-grupos anidados (paréntesis).")


RuleGroupDTO.model_rebuild()


class ConditionalRuleDTO(BaseModel):
    """Regla IF-THEN-ELSE completa con soporte para listas planas o Árbol AST."""

    rule_name: str = Field(description="Nombre identificador de la regla.")
    conditions: List[RuleConditionDTO] = Field(default_factory=list, description="Lista plana de condiciones (Legacy).")
    logical_operator: str = Field(default="AND", description="Operador lógico entre condiciones planas.")
    root_group: Optional[RuleGroupDTO] = Field(default=None, description="Nodo raíz del Árbol AST para sub-grupos anidados.")
    then_result_column: str = Field(description="Columna destino a crear/modificar.")
    then_value: str = Field(description="Valor asignado si la condición se cumple.")
    else_value: Optional[str] = Field(default="NORMAL", description="Valor por defecto si no se cumple.")


class RuleEvaluationResultDTO(BaseModel):
    """CU-10: Preview de evaluación de la regla sobre el Parquet."""

    rule_name: str
    result_column: str
    total_rows: int = 0
    matches_count: int = 0
    matches_percentage: float = 0.0
    sql_expression: str = Field(default="", description="Sentencia CASE WHEN generada.")
    sample_rows: List[dict] = Field(default_factory=list, description="Muestra de registros coincidentes.")
