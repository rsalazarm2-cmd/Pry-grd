"""Caso de Uso para Generar los Datamarts de la Capa Oro (CU-11, CU-12, CU-13).

Orquesta la ejecución del motor GoldDatamartEngine utilizando la conexión
compartida DuckDB.
"""

from src.gold.domain.gold_models_dto import GoldDatamartResultDTO
from src.gold.infrastructure.gold_datamart_engine import GoldDatamartEngine
from src.shared.api.dependencies import get_repository


class GenerateGoldModelsUseCase:
    """CU-11 / CU-12 / CU-13: Genera los datamarts Parquet de la Capa Oro."""

    def execute(
        self, silver_parquet_path: str, target_gold_dir: str
    ) -> GoldDatamartResultDTO:
        conn = get_repository().conn
        engine = GoldDatamartEngine(conn)
        return engine.generate_all_datamarts(silver_parquet_path, target_gold_dir)
