from src.shared.domain.journal_entry import DatasetProfileDTO
from src.shared.domain.journal_entry_repository import JournalEntryRepository


class ProfileDatasetUseCase:
    """Caso de uso para ejecutar el análisis exploratorio al 100% de la Capa Bronce."""

    def __init__(self, repository: JournalEntryRepository):
        self.repository = repository

    def execute(self, bronze_parquet_path: str) -> DatasetProfileDTO:
        profile = self.repository.get_bronze_profile(bronze_parquet_path)
        
        perfect_count = 0
        null_count = 0
        constant_count = 0

        for col in profile.columns:
            if col.unique_count <= 1:
                constant_count += 1
                col.status_label = "Constante"
                col.status_color = "rose"
            elif col.null_count > 0:
                null_count += 1
                col.status_label = "Nulos"
                col.status_color = "amber"
            else:
                perfect_count += 1
                col.status_label = "Perfecta"
                col.status_color = "emerald"

        profile.constant_columns_count = constant_count
        profile.null_columns_count = null_count
        profile.perfect_columns_count = perfect_count

        total_cells = profile.total_rows * profile.total_columns
        total_nulls = sum(col.null_count for col in profile.columns)

        if total_cells > 0:
            completeness = max(0.0, 100.0 - (total_nulls / total_cells * 100.0))
            profile.data_health_score = round(completeness, 1)
        else:
            profile.data_health_score = 100.0

        return profile
