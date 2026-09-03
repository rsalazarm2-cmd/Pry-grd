"""DTOs Pydantic para el Motor de Expresiones de Fecha y Separador de Montos.

Define los contratos de datos (Data Transfer Objects) que viajan entre
las capas Application ↔ Infrastructure ↔ API para los Casos de Uso
CU-01 (Redundancia de Fechas), CU-02 (Delta Segundos), CU-03 (Día Semana)
y CU-04 (Split Cargo/Abono).
"""

from pydantic import BaseModel, Field


class DatePairDTO(BaseModel):
    """Par de columnas de fecha seleccionadas por el auditor para análisis."""

    date_column_a: str = Field(description="Nombre de la primera columna de fecha.")
    date_column_b: str = Field(description="Nombre de la segunda columna de fecha.")


class HistogramBucketDTO(BaseModel):
    """Bucket de histograma para distribución de deltas temporales."""

    label: str = Field(description="Etiqueta del rango (ej. '0-60s').")
    count: int = Field(description="Cantidad de registros en este rango.")


class DateRedundancyResultDTO(BaseModel):
    """CU-01: Resultado de análisis de redundancia entre 2 columnas de fecha."""

    date_column_a: str
    date_column_b: str
    total_rows: int = 0
    matching_rows: int = 0
    match_percentage: float = Field(default=0.0, description="0.0 a 100.0")
    are_identical: bool = Field(default=False, description="True si match == 100%.")


class DateDeltaResultDTO(BaseModel):
    """CU-02: Resultado de cálculo de DIFERENCIA_SEGUNDOS entre 2 fechas."""

    source_column_a: str
    source_column_b: str
    result_column_name: str = "DIFERENCIA_SEGUNDOS_APROBACION"
    total_rows: int = 0
    min_delta_seconds: int = 0
    max_delta_seconds: int = 0
    avg_delta_seconds: float = 0.0
    rapid_approvals_count: int = Field(
        default=0, description="Registros con delta < 60 segundos."
    )
    histogram_buckets: list[HistogramBucketDTO] = Field(default_factory=list)


class WeekdayBucketDTO(BaseModel):
    """Bucket de distribución por día de la semana."""

    day: str = Field(description="Nombre del día (ej. 'LUNES').")
    count: int = Field(description="Cantidad de registros en este día.")


class WeekdayResultDTO(BaseModel):
    """CU-03: Resultado de derivación de día de semana + flag fin de semana."""

    source_column: str
    total_rows: int = 0
    weekend_count: int = 0
    weekend_percentage: float = 0.0
    weekday_distribution: list[WeekdayBucketDTO] = Field(default_factory=list)


class AmountSplitResultDTO(BaseModel):
    """CU-04: Resultado de separación de columna signada a CARGO/ABONO."""

    source_column: str
    cargo_column: str = "CARGO_DERIVADO"
    abono_column: str = "ABONO_DERIVADO"
    total_rows: int = 0
    rows_with_cargo: int = 0
    rows_with_abono: int = 0
    total_cargo: float = 0.0
    total_abono: float = 0.0
