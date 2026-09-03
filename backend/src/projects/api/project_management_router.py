"""Router API Ninja para la gestión de proyectos reales y eliminación segura.

Permite listar proyectos contables activos en disco (data/projects/) y eliminar
de forma segura los datos de un proyecto específico.
"""
import shutil
import logging
from pathlib import Path
from typing import List
from pydantic import BaseModel
from ninja import Router
from ninja.errors import HttpError
import duckdb
from src.shared.api.dependencies import get_project_repository

logger = logging.getLogger(__name__)
router = Router()

PROJECTS_BASE_DIR = Path("data/projects").resolve()


class ProjectInfoDTO(BaseModel):
    id: str
    name: str
    has_bronze: bool = False
    has_silver: bool = False
    silver_rows: int = 0
    created_at: str = ""


@router.get("/list", response=List[ProjectInfoDTO], tags=["Project Management"])
def list_projects(request):
    """Lista dinámicamente los proyectos contables reales existentes en disco."""
    if not PROJECTS_BASE_DIR.exists():
        PROJECTS_BASE_DIR.mkdir(parents=True, exist_ok=True)
        return []

    projects: List[ProjectInfoDTO] = []
    conn = duckdb.connect()

    for item in PROJECTS_BASE_DIR.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            bronze_file = item / "bronze" / "bronze.parquet"
            silver_file = item / "silver" / "silver.parquet"

            has_bronze = bronze_file.exists()
            has_silver = silver_file.exists()
            silver_rows = 0

            if has_silver:
                try:
                    safe_silver = str(silver_file.resolve()).replace("'", "''")
                    silver_rows = conn.execute(f"SELECT COUNT(*) FROM read_parquet('{safe_silver}')").fetchone()[0]
                except Exception:
                    silver_rows = 0

            projects.append(
                ProjectInfoDTO(
                    id=item.name,
                    name=item.name.replace("_", " ").title(),
                    has_bronze=has_bronze,
                    has_silver=has_silver,
                    silver_rows=silver_rows,
                )
            )

    conn.close()
    return projects


@router.delete("/{project_id}", response=dict, tags=["Project Management"])
def delete_project(request, project_id: str):
    """Elimina de forma segura un proyecto contable completo en disco."""
    p_repo = get_project_repository()
    slug = p_repo._slugify(project_id)
    success = p_repo.delete_project(slug)

    if not success:
        project_dir = PROJECTS_BASE_DIR / slug
        if project_dir.exists():
            shutil.rmtree(project_dir, ignore_errors=True)
            success = True
        else:
            raise HttpError(404, f"El proyecto '{project_id}' no existe.")

    logger.info(f"🗑️ Proyecto '{slug}' eliminado exitosamente de disco.")
    return {"status": "success", "message": f"Proyecto '{slug}' eliminado correctamente."}
