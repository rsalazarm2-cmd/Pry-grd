"""Casos de Uso de Fase 1: Expresiones de Fecha y Separación de Montos.

Orquestadores thin que inyectan la conexión DuckDB, instancian el engine
correspondiente, y delegan la ejecución. Cumplen SRP: cada clase es 1 CU.
"""

from src.silver.domain.date_expression_ast import (
    AmountSplitResultDTO,
    DateDeltaResultDTO,
    DateRedundancyResultDTO,
    WeekdayResultDTO,
)
from src.silver.infrastructure.silver_amount_splitter_engine import (
    SilverAmountSplitterEngine,
)
from src.silver.infrastructure.silver_date_expression_engine import (
    SilverDateExpressionEngine,
)
from src.shared.api.dependencies import get_repository


def _get_date_engine() -> SilverDateExpressionEngine:
    """Crea el engine de fechas con la conexión DuckDB compartida."""
    return SilverDateExpressionEngine(get_repository().conn)


def _get_split_engine() -> SilverAmountSplitterEngine:
    """Crea el engine de split con la conexión DuckDB compartida."""
    return SilverAmountSplitterEngine(get_repository().conn)


class ComputeDateRedundancyUseCase:
    """CU-01: Calcula % de redundancia entre 2 columnas de fecha."""

    def execute(
        self, parquet_path: str, col_a: str, col_b: str
    ) -> DateRedundancyResultDTO:
        """Ejecuta el cálculo de redundancia de fechas."""
        return _get_date_engine().compute_date_redundancy(parquet_path, col_a, col_b)


class ComputeDateDeltaUseCase:
    """CU-02: Genera estadísticas de DIFERENCIA_SEGUNDOS entre 2 fechas."""

    def execute(
        self, parquet_path: str, col_a: str, col_b: str
    ) -> DateDeltaResultDTO:
        """Ejecuta el cálculo de deltas temporales con histograma."""
        return _get_date_engine().compute_date_delta(parquet_path, col_a, col_b)


class ComputeWeekdayDistributionUseCase:
    """CU-03: Calcula distribución de día de semana + flag fin de semana."""

    def execute(self, parquet_path: str, date_column: str) -> WeekdayResultDTO:
        """Ejecuta la derivación de día de semana."""
        return _get_date_engine().compute_weekday_distribution(
            parquet_path, date_column
        )


class PreviewAmountSplitUseCase:
    """CU-04: Preview de separación de columna signada a Cargo/Abono."""

    def execute(self, parquet_path: str, source_column: str) -> AmountSplitResultDTO:
        """Ejecuta el preview de split sin persistir."""
        return _get_split_engine().preview_amount_split(parquet_path, source_column)


class ListDateColumnsUseCase:
    """Auxiliar: Lista columnas DATE/TIMESTAMP detectadas."""

    def execute(self, parquet_path: str) -> list[str]:
        """Retorna nombres de columnas de fecha."""
        return _get_date_engine().list_date_columns(parquet_path)


class ListNumericColumnsUseCase:
    """Auxiliar: Lista columnas numéricas detectadas."""

    def execute(self, parquet_path: str) -> list[str]:
        """Retorna nombres de columnas numéricas."""
        return _get_split_engine().list_numeric_columns(parquet_path)
