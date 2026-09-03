"""Pruebas Unitarias para el Módulo de Firma Criptográfica SHA-256 y RBAC (Fase 4)."""

from pathlib import Path
import pytest
from src.core.infrastructure.cryptographic_service import CryptographicAuditService, RBACService


def test_sha256_computation_and_receipt(test_data_dir: Path):
    """Verifica que el servicio calcule firmas SHA-256 inmutables de 64 caracteres."""
    sample_file = test_data_dir / "sample_crypto.txt"
    sample_file.write_text("EVIDENCIA_CONTABLE_INMUTABLE_SHA256")

    svc = CryptographicAuditService()
    file_hash = svc.compute_file_sha256(str(sample_file))

    assert len(file_hash) == 64
    assert file_hash != "0" * 64

    recipe = {"rules": ["TRIM", "UPPERCASE"]}
    receipt = svc.generate_receipt(str(sample_file), recipe_data=recipe, row_count=100)

    assert receipt.integrity_status == "VERIFIED"
    assert len(receipt.recipe_hash_sha256) == 64
    assert receipt.row_count == 100


def test_rbac_roles_permissions():
    """Verifica el mapa de permisos por rol (AUDITOR, SUPERVISOR, ADMIN)."""
    auditor_perm = RBACService.get_role_permissions("AUDITOR")
    assert auditor_perm.can_view_records is True
    assert auditor_perm.can_edit_recipes is False
    assert auditor_perm.can_manage_projects is False

    admin_perm = RBACService.get_role_permissions("ADMIN")
    assert admin_perm.can_edit_recipes is True
    assert admin_perm.can_manage_projects is True
