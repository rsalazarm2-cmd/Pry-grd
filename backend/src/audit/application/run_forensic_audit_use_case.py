"""Caso de Uso para Ejecutar la Auditoría Forense Integral (CU-16 a CU-19).

Orquesta la evaluación del ForensicAuditEngine utilizando la conexión DuckDB.
"""

from pathlib import Path
from src.audit.domain.forensic_dto import ForensicAuditMatrixDTO
from src.audit.infrastructure.forensic_audit_engine import ForensicAuditEngine
from src.shared.api.dependencies import get_repository


class RunForensicAuditUseCase:
    """Caso de Uso de Auditoría Forense Integral."""

    def execute(self, silver_parquet_path: str) -> ForensicAuditMatrixDTO:
        conn = get_repository().conn
        engine = ForensicAuditEngine(conn)
        return engine.run_full_forensic_audit(Path(silver_parquet_path))
