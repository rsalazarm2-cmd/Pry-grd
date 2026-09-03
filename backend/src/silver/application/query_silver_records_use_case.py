from src.shared.domain.journal_entry import TabularResultDTO
from src.shared.domain.journal_entry_repository import JournalEntryRepository


class QuerySilverRecordsUseCase:
    """Caso de uso para consultar registros de la Capa Plata con filtro opcional por QUALITY_STATUS."""

    def __init__(self, repository: JournalEntryRepository):
        self.repository = repository

    def execute(
        self,
        silver_parquet_path: str,
        quality_status: str = None,
        limit: int = 50,
        search: str = None,
        column_name: str = None,
        filters_json: str = None,
        view_mode: str = "ALL",
    ) -> TabularResultDTO:
        return self.repository.get_silver_records(
            silver_parquet_path, quality_status, limit, search, column_name, filters_json, view_mode
        )

