from src.project.domain.project import ProjectDTO, CreateProjectDTO
from src.project.domain.project_repository import ProjectRepository


class CreateProjectUseCase:
    """Caso de uso para registrar un nuevo proyecto con almacenamiento aislado."""

    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository

    def execute(self, dto: CreateProjectDTO) -> ProjectDTO:
        return self.project_repository.create_project(dto)
