from src.shared.domain.journal_entry import TabularResultDTO
from src.shared.domain.journal_entry_repository import JournalEntryRepository


class QueryGoldBalancesUseCase:
    """Caso de uso para consultar la tabla de balances agregados de la Capa Oro."""

    def __init__(self, repository: JournalEntryRepository):
        self.repository = repository

    def execute(self, gold_parquet_path: str, search: str = None, column_name: str = None, filters_json: str = None) -> TabularResultDTO:
        return self.repository.get_gold_balances(gold_parquet_path, search, column_name, filters_json)
