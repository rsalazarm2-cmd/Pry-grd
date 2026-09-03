"""API Router para el Módulo de Pista de Auditoría Criptográfica (SHA-256) y RBAC (Fase 4)."""

from typing import Optional
from ninja import Router, Query
from src.core.domain.audit_trail_dto import CryptographicReceiptDTO, UserRolePermissionDTO
from src.core.infrastructure.cryptographic_service import CryptographicAuditService, RBACService
from src.shared.api.dependencies import resolve_project_paths

router = Router(tags=["Gobernanza & Audit Trail (SHA-256)"])


@router.get("/audit-receipt", response=CryptographicReceiptDTO)
def get_cryptographic_receipt(request, project_id: Optional[str] = Query(None)):
    """Obtiene el recibo inmutable con firmas SHA-256 del Parquet y la Receta activa."""
    paths = resolve_project_paths(project_id)
    target = paths["silver"] if paths["silver"].exists() else paths["bronze"]
    row_cnt = 0
    if target.exists():
        import duckdb
        conn = duckdb.connect(":memory:")
        row_cnt = conn.execute(f"SELECT COUNT(*) FROM read_parquet('{target}')").fetchone()[0]

    svc = CryptographicAuditService()
    return svc.generate_receipt(str(target), row_count=row_cnt)


@router.get("/rbac-permissions", response=UserRolePermissionDTO)
def get_role_permissions(request, role: str = Query("AUDITOR")):
    """Consulta los permisos otorgados a un rol de usuario (AUDITOR, SUPERVISOR, ADMIN)."""
    return RBACService.get_role_permissions(role)
