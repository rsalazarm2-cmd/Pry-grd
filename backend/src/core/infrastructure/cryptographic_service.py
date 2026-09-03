"""Servicio de Firmado Criptográfico SHA-256 y Registro de Cadena de Custodia.

Calcula huellas digitales inmutables de Parquet y Recetas .json
para cumplimiento de auditoría forense sin repudio (Fase 4).
"""

import hashlib
import json
from pathlib import Path
from typing import Optional
from src.core.domain.audit_trail_dto import (
    AuditTrailEntryDTO,
    CryptographicReceiptDTO,
    UserRolePermissionDTO,
)


class CryptographicAuditService:
    """Servicio de verificación de integridad por firmas SHA-256."""

    @staticmethod
    def compute_file_sha256(file_path: str) -> str:
        """Calcula el hash SHA-256 de un archivo en disco.

        Args:
            file_path: Ruta del archivo.

        Returns:
            String hexadecimal de 64 caracteres SHA-256.
        """
        path = Path(file_path)
        if not path.exists():
            return "0" * 64

        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def compute_dict_sha256(data: dict) -> str:
        """Calcula el hash SHA-256 de una receta de transformación en memoria."""
        encoded = json.dumps(data, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def generate_receipt(
        self, parquet_path: str, recipe_data: Optional[dict] = None, row_count: int = 0
    ) -> CryptographicReceiptDTO:
        """Genera un recibo criptográfico inmutable firmado con SHA-256.

        Args:
            parquet_path: Ruta del Parquet activo.
            recipe_data: Receta JSON de transformación opcional.
            row_count: Cantidad de filas registradas.

        Returns:
            Objeto CryptographicReceiptDTO con firmas inmutables.
        """
        pq_hash = self.compute_file_sha256(parquet_path)
        rec_hash = (
            self.compute_dict_sha256(recipe_data)
            if recipe_data
            else "0" * 64
        )

        return CryptographicReceiptDTO(
            recipe_hash_sha256=rec_hash,
            dataset_hash_sha256=pq_hash,
            row_count=row_count,
            integrity_status="VERIFIED" if pq_hash != ("0" * 64) else "UNVERIFIED",
        )


class RBACService:
    """Servicio de Control de Acceso Basado en Roles (RBAC)."""

    ROLES: dict = {
        "AUDITOR": UserRolePermissionDTO(
            role_name="AUDITOR",
            can_view_records=True,
            can_edit_recipes=False,
            can_run_transformations=False,
            can_export_reports=True,
            can_manage_projects=False,
        ),
        "SUPERVISOR": UserRolePermissionDTO(
            role_name="SUPERVISOR",
            can_view_records=True,
            can_edit_recipes=True,
            can_run_transformations=True,
            can_export_reports=True,
            can_manage_projects=False,
        ),
        "ADMIN": UserRolePermissionDTO(
            role_name="ADMIN",
            can_view_records=True,
            can_edit_recipes=True,
            can_run_transformations=True,
            can_export_reports=True,
            can_manage_projects=True,
        ),
    }

    @classmethod
    def get_role_permissions(cls, role_name: str) -> UserRolePermissionDTO:
        """Obtiene las autorizaciones asignadas a un rol."""
        role_upper = (role_name or "AUDITOR").upper()
        return cls.ROLES.get(role_upper, cls.ROLES["AUDITOR"])

    @classmethod
    def check_permission(cls, role_name: str, permission_attribute: str) -> bool:
        """Verifica si el rol cuenta con un permiso específico."""
        perms = cls.get_role_permissions(role_name)
        return getattr(perms, permission_attribute, False)
