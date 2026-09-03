from src.shared.domain.journal_entry import TabularResultDTO
from src.shared.domain.journal_entry_repository import JournalEntryRepository


class QueryBronzeRecordsUseCase:
    """Caso de uso para consultar registros crudos de la Capa Bronce."""

    def __init__(self, repository: JournalEntryRepository):
        self.repository = repository

    def execute(self, bronze_parquet_path: str, limit: int = 50, search: str = None, column_name: str = None, filters_json: str = None) -> TabularResultDTO:
        return self.repository.get_bronze_records(bronze_parquet_path, limit, search, column_name, filters_json)
