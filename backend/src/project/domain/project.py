from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from src.shared.domain.journal_entry import TransformationRulesDTO


class ProjectDTO(BaseModel):
    """DTO que representa un Proyecto de Datamart Financiero aislado."""
    id: str = Field(..., description="Slug identificador único del proyecto (ej: contabilidad-2025)")
    name: str = Field(..., description="Nombre descriptivo del proyecto")
    description: Optional[str] = Field(default="", description="Descripción del dominio del proyecto")
    domain: str = Field(default="GENERAL_LEDGER", description="Dominio ERP (ej: GENERAL_LEDGER, PAYROLL, SALES)")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Fecha de creación ISO 8601")
    storage_path: str = Field(..., description="Ruta absoluta al directorio aislado del proyecto")
    has_recipe: bool = Field(default=False, description="Indica si existe una receta de limpieza persistente guardada")


class CreateProjectDTO(BaseModel):
    """DTO para la creación de un nuevo proyecto."""
    name: str = Field(..., min_length=2, max_length=100, description="Nombre del proyecto")
    description: Optional[str] = Field(default="", description="Descripción opcional")
    domain: Optional[str] = Field(default="GENERAL_LEDGER", description="Dominio ERP")


class ProjectRecipeDTO(BaseModel):
    """DTO que encapsula la Receta de Limpieza Persistente reutilizable."""
    project_id: str = Field(..., description="Identificador del proyecto")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Fecha de última actualización ISO 8601")
    rules: TransformationRulesDTO = Field(..., description="Reglas completas de limpieza, tipado e imputación")
