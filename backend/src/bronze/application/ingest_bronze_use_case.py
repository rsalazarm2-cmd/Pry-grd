from src.shared.domain.journal_entry import BronzeIngestionResultDTO
from src.shared.domain.journal_entry_repository import JournalEntryRepository


class IngestBronzeDataUseCase:
    """Caso de uso para ingestar un CSV crudo a la Capa Bronce en formato Parquet."""

    def __init__(self, repository: JournalEntryRepository):
        self.repository = repository

    def execute(self, source_csv_path: str, target_parquet_path: str) -> BronzeIngestionResultDTO:
        return self.repository.save_bronze(source_csv_path, target_parquet_path)
