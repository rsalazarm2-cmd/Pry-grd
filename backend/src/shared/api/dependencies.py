import os
from typing import Any, Dict, Optional
from src.shared.infrastructure.duckdb_journal_repository import DuckDBJournalRepository
from src.project.infrastructure.duckdb_project_repository import DuckDBProjectRepository
from src.shared.infrastructure.project_path_resolver import resolve_medallion_paths

def get_repository() -> DuckDBJournalRepository:
    return DuckDBJournalRepository()

def get_project_repository() -> DuckDBProjectRepository:
    return DuckDBProjectRepository()

def resolve_project_paths(project_id: Optional[str] = None) -> Dict[str, Any]:
    """Resuelve las rutas físicas Medallion usando el resolver modular atómico."""
    base_dir = os.path.abspath("data/projects")
    return resolve_medallion_paths(base_dir, project_id)
