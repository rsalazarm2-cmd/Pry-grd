from abc import ABC, abstractmethod
from typing import List, Optional
from src.project.domain.project import ProjectDTO, CreateProjectDTO, ProjectRecipeDTO
from src.shared.domain.journal_entry import TransformationRulesDTO


class ProjectRepository(ABC):
    """Interfaz abstracta (Puerto) para la gestión CRUD de Proyectos y Recetas de Limpieza."""

    @abstractmethod
    def list_projects(self) -> List[ProjectDTO]:
        """Obtiene la lista de proyectos registrados."""
        pass

    @abstractmethod
    def get_project(self, project_id: str) -> Optional[ProjectDTO]:
        """Obtiene un proyecto por su identificador slug."""
        pass

    @abstractmethod
    def create_project(self, dto: CreateProjectDTO) -> ProjectDTO:
        """Crea un nuevo proyecto con almacenamiento aislado."""
        pass

    @abstractmethod
    def delete_project(self, project_id: str) -> bool:
        """Elimina un proyecto y su almacenamiento aislado."""
        pass

    @abstractmethod
    def get_recipe(self, project_id: str) -> Optional[TransformationRulesDTO]:
        """Obtiene la receta de limpieza persistente de un proyecto si existe."""
        pass

    @abstractmethod
    def save_recipe(self, project_id: str, rules: TransformationRulesDTO) -> ProjectRecipeDTO:
        """Guarda o actualiza la receta de limpieza persistente de un proyecto."""
        pass
