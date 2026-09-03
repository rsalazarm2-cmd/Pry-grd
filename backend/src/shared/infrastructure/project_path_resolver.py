import os
from pathlib import Path
from typing import Dict, Any, Optional
from src.project.domain.project import ProjectDTO

def resolve_medallion_paths(base_projects_dir: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Servidor atómico modular que resuelve limpiamente las rutas físicas de los datasets Bronce, Plata y Oro.
    Aplica tolerancia a fallos si metadata.json se encuentra en raíz o dentro de silver.
    """
    clean_id = (project_id or "proyecto-principal").lower().strip()
    slug = clean_id.replace(" ", "-")
    
    folder_path = Path(base_projects_dir) / slug
    if not folder_path.exists():
        # Búsqueda insensible a mayúsculas si no coincide el slug exacto
        if os.path.exists(base_projects_dir):
            for item in os.listdir(base_projects_dir):
                if item.lower() == slug.lower() or item.lower() == clean_id:
                    folder_path = Path(base_projects_dir) / item
                    break

    os.makedirs(folder_path / "bronze", exist_ok=True)
    os.makedirs(folder_path / "silver", exist_ok=True)
    os.makedirs(folder_path / "gold", exist_ok=True)

    project = ProjectDTO(
        id=slug,
        name=project_id or "Proyecto Principal",
        description="Dataset Medallion Financiero ERP",
        domain="GENERAL_LEDGER",
        created_at="",
        storage_path=str(folder_path),
        has_recipe=(folder_path / "recipe.json").exists() or (folder_path / "silver" / "recipe.json").exists()
    )

    return {
        "project": project,
        "bronze": folder_path / "bronze" / "bronze.parquet",
        "silver": folder_path / "silver" / "silver.parquet",
        "gold_dir": folder_path / "gold",
        "gold_ledger": folder_path / "gold" / "gold_balance_by_ledger.parquet",
        "gold_account": folder_path / "gold" / "gold_balance_by_account.parquet",
    }
