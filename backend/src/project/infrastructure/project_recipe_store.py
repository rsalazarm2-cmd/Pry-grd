import os
import json
from datetime import datetime
from typing import Optional
from src.project.domain.project import ProjectRecipeDTO
from src.shared.domain.journal_entry import TransformationRulesDTO

def get_project_recipe(projects_dir: str, slug: str) -> Optional[TransformationRulesDTO]:
    recipe_path = os.path.join(projects_dir, slug, "recipe.json")
    if not os.path.exists(recipe_path):
        return None

    try:
        with open(recipe_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        rules_dict = data.get("rules", data)
        return TransformationRulesDTO(**rules_dict)
    except Exception:
        return None

def save_project_recipe(projects_dir: str, slug: str, rules: TransformationRulesDTO) -> ProjectRecipeDTO:
    folder_path = os.path.join(projects_dir, slug)
    os.makedirs(folder_path, exist_ok=True)

    recipe_path = os.path.join(folder_path, "recipe.json")
    recipe_data = {
        "project_id": slug,
        "updated_at": datetime.now().isoformat(),
        "rules": rules.model_dump()
    }

    with open(recipe_path, "w", encoding="utf-8") as f:
        json.dump(recipe_data, f, indent=2, ensure_ascii=False)

    return ProjectRecipeDTO(
        project_id=slug,
        updated_at=recipe_data["updated_at"],
        rules=rules
    )
