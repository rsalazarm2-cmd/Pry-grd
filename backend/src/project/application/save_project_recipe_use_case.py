from src.project.domain.project import ProjectRecipeDTO
from src.shared.domain.journal_entry import TransformationRulesDTO
from src.project.domain.project_repository import ProjectRepository


class SaveProjectRecipeUseCase:
    """Caso de uso para guardar la receta de limpieza reutilizable de un proyecto."""

    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository

    def execute(self, project_id: str, rules: TransformationRulesDTO) -> ProjectRecipeDTO:
        return self.project_repository.save_recipe(project_id, rules)
