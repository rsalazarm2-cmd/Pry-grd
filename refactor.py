import os
import shutil
from pathlib import Path

# Config
SRC_DIR = Path("/run/media/rsalazar/Ronald/Python/Pry Grd/backend/src")

# Target slices
SLICES = ["bronze", "silver", "gold", "project", "shared"]

# File mapping (source -> target)
# Source paths relative to SRC_DIR
MAPPING = {
    # BRONZE
    "application/use_cases/ingest_bronze_use_case.py": "bronze/application/ingest_bronze_use_case.py",
    "application/use_cases/profile_dataset_use_case.py": "bronze/application/profile_dataset_use_case.py",
    "application/use_cases/query_bronze_records_use_case.py": "bronze/application/query_bronze_records_use_case.py",
    "infrastructure/duckdb/bronze_service.py": "bronze/infrastructure/bronze_service.py",
    
    # SILVER
    "application/use_cases/transform_silver_use_case.py": "silver/application/transform_silver_use_case.py",
    "application/use_cases/query_silver_records_use_case.py": "silver/application/query_silver_records_use_case.py",
    "domain/entities/atomicity.py": "silver/domain/atomicity.py",
    "domain/services/atomicity_analyzer.py": "silver/domain/atomicity_analyzer.py",
    "infrastructure/duckdb/silver_service.py": "silver/infrastructure/silver_service.py",
    "infrastructure/duckdb/atomicity_service.py": "silver/infrastructure/atomicity_service.py",
    
    # GOLD
    "application/use_cases/generate_gold_use_case.py": "gold/application/generate_gold_use_case.py",
    "application/use_cases/query_gold_balances_use_case.py": "gold/application/query_gold_balances_use_case.py",
    "application/use_cases/query_gold_account_balances_use_case.py": "gold/application/query_gold_account_balances_use_case.py",
    "infrastructure/duckdb/gold_service.py": "gold/infrastructure/gold_service.py",
    
    # PROJECT
    "api/routers/project_router.py": "project/api/project_router.py",
    "application/use_cases/project/create_project_use_case.py": "project/application/create_project_use_case.py",
    "application/use_cases/project/delete_project_use_case.py": "project/application/delete_project_use_case.py",
    "application/use_cases/project/list_projects_use_case.py": "project/application/list_projects_use_case.py",
    "application/use_cases/project/save_project_recipe_use_case.py": "project/application/save_project_recipe_use_case.py",
    "domain/entities/project.py": "project/domain/project.py",
    "domain/repositories/project_repository.py": "project/domain/project_repository.py",
    "infrastructure/repositories/duckdb_project_repository.py": "project/infrastructure/duckdb_project_repository.py",
    
    # SHARED / ORCHESTRATOR
    "api/routers/medallion_router.py": "shared/api/medallion_router.py",
    "api/routers/health_router.py": "shared/api/health_router.py",
    "application/use_cases/execute_pipeline_use_case.py": "shared/application/execute_pipeline_use_case.py",
    "domain/entities/journal_entry.py": "shared/domain/journal_entry.py", # For now keep DTOs here
    "domain/repositories/journal_entry_repository.py": "shared/domain/journal_entry_repository.py",
    "infrastructure/duckdb/engine.py": "shared/infrastructure/engine.py",
    "infrastructure/duckdb/query_builder.py": "shared/infrastructure/query_builder.py",
    "infrastructure/repositories/duckdb_journal_repository.py": "shared/infrastructure/duckdb_journal_repository.py",
}

# The files in `api` that are at the root (urls.py, views.py) can stay in shared or move to a `core` or `main` folder.
# Let's keep a `core` folder for FastAPI setup.
MAPPING.update({
    "api/urls.py": "core/urls.py",
    "api/views.py": "core/views.py",
})

# Maps old import path substrings to new import path substrings
IMPORT_MAPPINGS = {
    # Application Bronze
    "src.application.use_cases.ingest_bronze_use_case": "src.bronze.application.ingest_bronze_use_case",
    "src.application.use_cases.profile_dataset_use_case": "src.bronze.application.profile_dataset_use_case",
    "src.application.use_cases.query_bronze_records_use_case": "src.bronze.application.query_bronze_records_use_case",
    # Infra Bronze
    "src.infrastructure.duckdb.bronze_service": "src.bronze.infrastructure.bronze_service",
    
    # Application Silver
    "src.application.use_cases.transform_silver_use_case": "src.silver.application.transform_silver_use_case",
    "src.application.use_cases.query_silver_records_use_case": "src.silver.application.query_silver_records_use_case",
    # Domain Silver
    "src.domain.entities.atomicity": "src.silver.domain.atomicity",
    "src.domain.services.atomicity_analyzer": "src.silver.domain.atomicity_analyzer",
    # Infra Silver
    "src.infrastructure.duckdb.silver_service": "src.silver.infrastructure.silver_service",
    "src.infrastructure.duckdb.atomicity_service": "src.silver.infrastructure.atomicity_service",
    
    # Application Gold
    "src.application.use_cases.generate_gold_use_case": "src.gold.application.generate_gold_use_case",
    "src.application.use_cases.query_gold_balances_use_case": "src.gold.application.query_gold_balances_use_case",
    "src.application.use_cases.query_gold_account_balances_use_case": "src.gold.application.query_gold_account_balances_use_case",
    # Infra Gold
    "src.infrastructure.duckdb.gold_service": "src.gold.infrastructure.gold_service",
    
    # Application Project
    "src.application.use_cases.project.create_project_use_case": "src.project.application.create_project_use_case",
    "src.application.use_cases.project.delete_project_use_case": "src.project.application.delete_project_use_case",
    "src.application.use_cases.project.list_projects_use_case": "src.project.application.list_projects_use_case",
    "src.application.use_cases.project.save_project_recipe_use_case": "src.project.application.save_project_recipe_use_case",
    "src.application.use_cases.project": "src.project.application",
    # Domain Project
    "src.domain.entities.project": "src.project.domain.project",
    "src.domain.repositories.project_repository": "src.project.domain.project_repository",
    # Infra Project
    "src.infrastructure.repositories.duckdb_project_repository": "src.project.infrastructure.duckdb_project_repository",
    
    # Shared
    "src.api.routers.medallion_router": "src.shared.api.medallion_router",
    "src.api.routers.health_router": "src.shared.api.health_router",
    "src.application.use_cases.execute_pipeline_use_case": "src.shared.application.execute_pipeline_use_case",
    "src.domain.entities.journal_entry": "src.shared.domain.journal_entry",
    "src.domain.repositories.journal_entry_repository": "src.shared.domain.journal_entry_repository",
    "src.infrastructure.duckdb.engine": "src.shared.infrastructure.engine",
    "src.infrastructure.duckdb.query_builder": "src.shared.infrastructure.query_builder",
    "src.infrastructure.repositories.duckdb_journal_repository": "src.shared.infrastructure.duckdb_journal_repository",
    
    # Core
    "src.api.urls": "src.core.urls",
    "src.api.views": "src.core.views",
}

def main():
    # 1. Create target directories and __init__.py files
    for slice_name in SLICES + ["core"]:
        for layer in ["api", "application", "domain", "infrastructure"]:
            dir_path = SRC_DIR / slice_name / layer
            dir_path.mkdir(parents=True, exist_ok=True)
            (dir_path / "__init__.py").touch()
        (SRC_DIR / slice_name / "__init__.py").touch()
        
    # 2. Move files
    for src_rel, tgt_rel in MAPPING.items():
        src_path = SRC_DIR / src_rel
        tgt_path = SRC_DIR / tgt_rel
        if src_path.exists():
            tgt_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(tgt_path))
            print(f"Moved {src_rel} -> {tgt_rel}")
        else:
            print(f"WARNING: File not found {src_path}")
            
    # 3. Update imports in all python files in SRC_DIR
    for root, dirs, files in os.walk(SRC_DIR):
        for file in files:
            if not file.endswith(".py"):
                continue
            filepath = Path(root) / file
            
            with open(filepath, "r") as f:
                content = f.read()
                
            original_content = content
            for old_import, new_import in IMPORT_MAPPINGS.items():
                content = content.replace(old_import, new_import)
                
            # Also replace generic module imports that might have been shortened
            # e.g. from src.domain.entities import ...
            content = content.replace("from src.domain.entities import", "from src.shared.domain.journal_entry import")
            
            if content != original_content:
                with open(filepath, "w") as f:
                    f.write(content)
                print(f"Updated imports in {filepath.relative_to(SRC_DIR)}")

    # 4. Clean up old empty directories
    for old_dir in ["api", "application", "domain", "infrastructure"]:
        old_path = SRC_DIR / old_dir
        if old_path.exists():
            # Delete recursively
            shutil.rmtree(old_path, ignore_errors=True)
            print(f"Deleted old directory {old_dir}")

if __name__ == "__main__":
    main()
