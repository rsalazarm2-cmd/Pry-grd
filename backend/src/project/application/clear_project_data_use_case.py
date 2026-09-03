from src.project.domain.project_repository import ProjectRepository

class ClearProjectDataUseCase:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def execute(self, project_id: str) -> bool:
        """
        Limpia los datos ingestados y tablas Medallion de un proyecto, 
        conservando su configuración y metadata.
        """
        return self.repository.clear_project_data(project_id)
