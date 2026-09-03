import json
import logging
import os
import re
import shutil
from datetime import datetime
from typing import List, Optional

from src.project.domain.project import ProjectDTO, CreateProjectDTO, ProjectRecipeDTO
from src.shared.domain.journal_entry import TransformationRulesDTO
from src.project.domain.project_repository import ProjectRepository
from src.project.infrastructure.project_recipe_store import get_project_recipe, save_project_recipe

logger = logging.getLogger(__name__)

class DuckDBProjectRepository(ProjectRepository):
    """Adaptador de Infraestructura para la gestión física de Proyectos y Recetas en disco."""

    def __init__(self, base_data_dir: str = "data"):
        self.base_data_dir = os.path.abspath(base_data_dir)
        self.projects_dir = os.path.join(self.base_data_dir, "projects")
        os.makedirs(self.projects_dir, exist_ok=True)

    def _slugify(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_-]+', '-', text)
        return text or "proyecto"

    def list_projects(self) -> List[ProjectDTO]:
        projects = []
        if not os.path.exists(self.projects_dir):
            return projects

        for folder_name in sorted(os.listdir(self.projects_dir)):
            folder_path = os.path.join(self.projects_dir, folder_name)
            meta_path = os.path.join(folder_path, "metadata.json")
            silver_meta_path = os.path.join(folder_path, "silver", "metadata.json")
            target_meta = meta_path if os.path.exists(meta_path) else (silver_meta_path if os.path.exists(silver_meta_path) else None)

            if os.path.isdir(folder_path):
                meta = {}
                if target_meta:
                    try:
                        with open(target_meta, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                    except Exception as e:
                        logger.warning(f"No se pudo leer metadata en '{target_meta}': {e}")
                
                projects.append(ProjectDTO(
                    id=meta.get("id", folder_name),
                    name=meta.get("name", folder_name),
                    description=meta.get("description", ""),
                    domain=meta.get("domain", "GENERAL_LEDGER"),
                    created_at=meta.get("created_at", datetime.now().isoformat()),
                    storage_path=folder_path,
                    has_recipe=os.path.exists(os.path.join(folder_path, "recipe.json")) or os.path.exists(os.path.join(folder_path, "silver", "recipe.json"))
                ))

        return projects

    def get_project(self, project_id: str) -> Optional[ProjectDTO]:
        slug = self._slugify(project_id)
        folder_path = os.path.join(self.projects_dir, slug)
        
        if not os.path.exists(folder_path):
            # Probar búsqueda insensible a mayúsculas
            for folder_name in os.listdir(self.projects_dir):
                if folder_name.lower() == slug.lower() or folder_name.lower() == project_id.lower():
                    folder_path = os.path.join(self.projects_dir, folder_name)
                    slug = folder_name
                    break

        if not os.path.exists(folder_path):
            return None

        meta_path = os.path.join(folder_path, "metadata.json")
        silver_meta_path = os.path.join(folder_path, "silver", "metadata.json")
        target_meta = meta_path if os.path.exists(meta_path) else (silver_meta_path if os.path.exists(silver_meta_path) else None)

        meta = {}
        if target_meta:
            try:
                with open(target_meta, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception as e:
                logger.warning(f"Error al obtener metadata del proyecto '{project_id}': {e}")

        return ProjectDTO(
            id=meta.get("id", slug),
            name=meta.get("name", slug),
            description=meta.get("description", ""),
            domain=meta.get("domain", "GENERAL_LEDGER"),
            created_at=meta.get("created_at", datetime.now().isoformat()),
            storage_path=folder_path,
            has_recipe=os.path.exists(os.path.join(folder_path, "recipe.json")) or os.path.exists(os.path.join(folder_path, "silver", "recipe.json"))
        )


    def get_or_default(self, project_id: str) -> ProjectDTO:
        project = self.get_project(project_id)
        if project:
            return project

        projects = self.list_projects()
        if projects:
            return projects[0]

        return self.create_project(CreateProjectDTO(
            name="Proyecto Principal",
            description="Proyecto inicial del Datamart Financiero ERP",
            domain="GENERAL_LEDGER",
        ))

    def create_project(self, dto: CreateProjectDTO) -> ProjectDTO:
        slug = self._slugify(dto.name)
        folder_path = os.path.join(self.projects_dir, slug)

        if os.path.exists(folder_path):
            meta_path = os.path.join(folder_path, "metadata.json")
            if os.path.exists(meta_path):
                raise ValueError(f"Ya existe un proyecto con el nombre '{dto.name}'.")
            else:
                shutil.rmtree(folder_path, ignore_errors=True)
                os.makedirs(folder_path, exist_ok=True)
        else:
            os.makedirs(folder_path, exist_ok=True)

        os.makedirs(os.path.join(folder_path, "bronze"), exist_ok=True)
        os.makedirs(os.path.join(folder_path, "silver"), exist_ok=True)
        os.makedirs(os.path.join(folder_path, "gold"), exist_ok=True)

        metadata = {
            "id": slug,
            "name": dto.name,
            "description": dto.description or "",
            "domain": dto.domain or "GENERAL_LEDGER",
            "created_at": datetime.now().isoformat()
        }

        meta_path = os.path.join(folder_path, "metadata.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return ProjectDTO(
            id=slug,
            name=dto.name,
            description=dto.description or "",
            domain=dto.domain or "GENERAL_LEDGER",
            created_at=metadata["created_at"],
            storage_path=folder_path,
            has_recipe=False
        )

    def delete_project(self, project_id: str) -> bool:
        slug = self._slugify(project_id)
        folder_path = os.path.join(self.projects_dir, slug)

        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            meta_path = os.path.join(folder_path, "metadata.json")
            if os.path.exists(meta_path):
                try:
                    os.remove(meta_path)
                except OSError:
                    pass
            
            shutil.rmtree(folder_path, ignore_errors=True)
            return True
        return False

    def clear_project_data(self, project_id: str) -> bool:
        slug = self._slugify(project_id)
        folder_path = os.path.join(self.projects_dir, slug)

        if not (os.path.exists(folder_path) and os.path.isdir(folder_path)):
            return False

        for sub_dir in ["raw", "bronze", "silver", "gold"]:
            sub_path = os.path.join(folder_path, sub_dir)
            if os.path.exists(sub_path) and os.path.isdir(sub_path):
                shutil.rmtree(sub_path)
                
        os.makedirs(os.path.join(folder_path, "bronze"), exist_ok=True)
        os.makedirs(os.path.join(folder_path, "silver"), exist_ok=True)
        os.makedirs(os.path.join(folder_path, "gold"), exist_ok=True)

        return True

    def get_recipe(self, project_id: str) -> Optional[TransformationRulesDTO]:
        return get_project_recipe(self.projects_dir, self._slugify(project_id))

    def save_recipe(self, project_id: str, rules: TransformationRulesDTO) -> ProjectRecipeDTO:
        return save_project_recipe(self.projects_dir, self._slugify(project_id), rules)
