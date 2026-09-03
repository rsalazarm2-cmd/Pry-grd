from pydantic import BaseModel
from src.shared.domain.journal_entry import (
    BronzeIngestionResultDTO,
    DatasetProfileDTO,
    SilverTransformationResultDTO,
    BronzeToSilverRulesDTO,
)
from src.shared.domain.journal_entry_repository import JournalEntryRepository
from src.silver.application.transform_silver_use_case import TransformSilverDataUseCase

class PipelineExecutionSummaryDTO(BaseModel):
    bronze_result: BronzeIngestionResultDTO
    silver_result: SilverTransformationResultDTO
    total_pipeline_time_seconds: float


class ExecutePipelineUseCase:
    """Caso de uso orquestador que ejecuta el pipeline completo (Raw -> Bronce -> Plata)."""

    def __init__(self, repository: JournalEntryRepository):
        self.repository = repository

    def execute(
        self,
        raw_csv_path: str,
        bronze_parquet_path: str,
        silver_parquet_path: str,
        bronze_rules: BronzeToSilverRulesDTO = None,
    ) -> PipelineExecutionSummaryDTO:
        import time

        start_time = time.time()

        # 1. Ingesta a Capa Bronce
        bronze_res = self.repository.save_bronze(raw_csv_path, bronze_parquet_path)

        # 2. Bronce -> Plata
        silver_uc = TransformSilverDataUseCase(self.repository)
        t_res = silver_uc.execute(bronze_parquet_path, silver_parquet_path, bronze_rules)

        total_time = round(time.time() - start_time, 4)

        return PipelineExecutionSummaryDTO(
            bronze_result=bronze_res,
            silver_result=t_res,
            total_pipeline_time_seconds=total_time,
        )
