from src.shared.domain.journal_entry import TabularResultDTO
from src.shared.domain.journal_entry_repository import JournalEntryRepository


class QueryGoldAccountBalancesUseCase:
    """Caso de uso para consultar la tabla Oro de balances por cuenta contable (PyG)."""

    def __init__(self, repository: JournalEntryRepository):
        self.repository = repository

    def execute(self, gold_account_parquet_path: str, search: str = None, column_name: str = None, filters_json: str = None) -> TabularResultDTO:
        return self.repository.get_gold_account_balances(gold_account_parquet_path, search, column_name, filters_json)
