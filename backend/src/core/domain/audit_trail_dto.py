"""DTOs Pydantic para la Pista de Auditoría Criptográfica (SHA-256) y RBAC.

Garantiza la inmutabilidad de la cadena de custodia de evidencia contable
y el control de accesos por roles (Fase 4).
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CryptographicReceiptDTO(BaseModel):
    """Recibo criptográfico inmutable firmado con SHA-256."""

    recipe_hash_sha256: str = Field(description="Hash SHA-256 de la receta JSON de transformación.")
    dataset_hash_sha256: str = Field(description="Hash SHA-256 del Parquet activo.")
    row_count: int = Field(default=0, description="Total de registros verificados.")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    integrity_status: str = Field(default="VERIFIED", description="VERIFIED o TAMPERED.")


class AuditTrailEntryDTO(BaseModel):
    """Entrada inmutable del Log de Auditoría (Audit Trail)."""

    entry_id: str = Field(description="Identificador único del registro de auditoría.")
    user_id: str = Field(description="Usuario que ejecutó la acción.")
    user_role: str = Field(description="Rol del usuario (AUDITOR, SUPERVISOR, ADMIN).")
    action: str = Field(description="Acción realizada (TRANSFORM, PROMOTE, EVALUATE, EXPORT).")
    project_id: str = Field(description="ID del proyecto auditado.")
    receipt: CryptographicReceiptDTO
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class UserRolePermissionDTO(BaseModel):
    """Definición de rol y permisos RBAC."""

    role_name: str = Field(description="Nombre del rol: AUDITOR, SUPERVISOR, ADMIN.")
    can_view_records: bool = True
    can_edit_recipes: bool = False
    can_run_transformations: bool = False
    can_export_reports: bool = True
    can_manage_projects: bool = False
