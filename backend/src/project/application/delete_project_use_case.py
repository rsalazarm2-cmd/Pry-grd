from src.project.domain.project_repository import ProjectRepository


class DeleteProjectUseCase:
    """Caso de uso para eliminar un proyecto y su directorio en disco."""

    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository

    def execute(self, project_id: str) -> bool:
        return self.project_repository.delete_project(project_id)
