"""DTOs para el Motor de Linaje y Trazabilidad Transparente (CU-07).

Define los contratos para representar el flujo de metamorfosis de datos:
Columna Origen (Bronce) ➔ Regla / Transformación ➔ Columna Estandarizada (Plata).
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class LineageItemDTO(BaseModel):
    """Representa el linaje de 1 columna individual."""

    source_column: str = Field(description="Nombre de la columna en la Capa Bronce.")
    target_column: str = Field(description="Nombre de la columna en la Capa Plata.")
    inferred_type: str = Field(default="VARCHAR", description="Tipo inferido de origen.")
    target_type: str = Field(default="VARCHAR", description="Tipo destino en Plata.")
    null_imputation: str = Field(default="DEFAULT", description="Estrategia de imputación.")
    is_included: bool = Field(default=True, description="True si fue incluida en Plata.")
    quality_status: str = Field(default="OK", description="Estado de integridad (OK, WARN, TRAP).")


class LineageMatrixDTO(BaseModel):
    """Resumen completo del linaje de transformación del proyecto."""

    project_id: str
    source_columns_count: int = 0
    target_columns_count: int = 0
    recipe_applied: bool = Field(default=False, description="True si proviene de .column_mapping_rules.json.")
    items: List[LineageItemDTO] = Field(default_factory=list)
