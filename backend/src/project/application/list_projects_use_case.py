from typing import List
from src.project.domain.project import ProjectDTO
from src.project.domain.project_repository import ProjectRepository


class ListProjectsUseCase:
    """Caso de uso para listar todos los proyectos disponibles."""

    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository

    def execute(self) -> List[ProjectDTO]:
        return self.project_repository.list_projects()
