from typing import Dict, List, Optional
from ninja import Router
from ninja.errors import HttpError

from src.project.application.list_projects_use_case import ListProjectsUseCase
from src.project.application.create_project_use_case import CreateProjectUseCase
from src.project.application.delete_project_use_case import DeleteProjectUseCase
from src.project.application.save_project_recipe_use_case import SaveProjectRecipeUseCase
from src.project.application.clear_project_data_use_case import ClearProjectDataUseCase
from src.shared.domain.journal_entry import TransformationRulesDTO
from src.project.domain.project import (
    ProjectDTO,
    CreateProjectDTO,
    ProjectRecipeDTO,
)
from src.project.infrastructure.duckdb_project_repository import DuckDBProjectRepository

router = Router()


def get_project_repository() -> DuckDBProjectRepository:
    return DuckDBProjectRepository()


@router.get("/projects", response=List[ProjectDTO], tags=["Projects"])
def list_projects(request):
    """Lista todos los proyectos creados en el sistema."""
    use_case = ListProjectsUseCase(get_project_repository())
    return use_case.execute()


@router.post("/projects", response=ProjectDTO, tags=["Projects"])
def create_project(request, dto: CreateProjectDTO):
    """Crea un nuevo proyecto con almacenamiento Medallion aislado."""
    try:
        use_case = CreateProjectUseCase(get_project_repository())
        return use_case.execute(dto)
    except ValueError as e:
        raise HttpError(400, str(e))


@router.delete("/projects/{project_id}", response=Dict[str, bool], tags=["Projects"])
def delete_project(request, project_id: str):
    """Elimina un proyecto y su directorio aislado."""
    use_case = DeleteProjectUseCase(get_project_repository())
    success = use_case.execute(project_id)
    if not success:
        raise HttpError(404, f"Proyecto '{project_id}' no encontrado.")
    return {"success": True}


@router.post("/projects/{project_id}/clear-data", tags=["Projects"])
def clear_project_data(request, project_id: str):
    """Limpia los datos ingestados y tablas Medallion, conservando la configuración del proyecto."""
    use_case = ClearProjectDataUseCase(get_project_repository())
    success = use_case.execute(project_id)
    if not success:
        raise HttpError(404, f"No se pudo limpiar o no se encontró el proyecto '{project_id}'.")
    return {"message": f"Datos del proyecto '{project_id}' limpiados exitosamente. La configuración se conserva."}


@router.get("/projects/{project_id}/recipe", response=Optional[TransformationRulesDTO], tags=["Projects"])
def get_project_recipe(request, project_id: str):
    """Obtiene la receta de limpieza guardada de un proyecto."""
    p_repo = get_project_repository()
    return p_repo.get_recipe(project_id)


@router.post("/projects/{project_id}/recipe", response=ProjectRecipeDTO, tags=["Projects"])
def save_project_recipe(request, project_id: str, rules: TransformationRulesDTO):
    """Guarda o actualiza la receta de limpieza persistente reutilizable."""
    use_case = SaveProjectRecipeUseCase(get_project_repository())
    return use_case.execute(project_id, rules)
