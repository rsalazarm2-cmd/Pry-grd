"""DTOs Pydantic para el Análisis Universal de la Ley de Benford (Estándar Nigrini).

Soporta auditoría sobre cualquier base de datos (Oracle, SAP, SQL Server, Parquet)
con descubrimiento dinámico de columnas numéricas y análisis de 1er dígito, 2º dígito y 2 primeros dígitos.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class BenfordDigitDTO(BaseModel):
    """Punto de comparación entre la frecuencia observada y la teórica de Benford."""

    digit: int = Field(description="Dígito evaluado (1-9, 0-9 o 10-99).")
    expected_freq: float = Field(description="Frecuencia teórica esperada por la Ley de Benford (%).")
    actual_freq: float = Field(description="Frecuencia real observada en el dataset (%).")
    actual_count: int = Field(default=0, description="Conteo absoluto de apariciones.")
    deviation: float = Field(default=0.0, description="Desviación absoluta respecto a la norma (%).")
    is_anomalous: bool = Field(default=False, description="Verdadero si supera el umbral de tolerancia.")


class BenfordAnalysisResultDTO(BaseModel):
    """Resultado consolidado de la prueba forense de Benford."""

    column_analyzed: str = Field(description="Columna de monto evaluada.")
    total_samples: int = Field(default=0, description="Total de montos válidos analizados.")
    chi_square_stat: float = Field(default=0.0, description="Estadístico Chi-cuadrado acumulado.")
    mad_score: float = Field(default=0.0, description="Desviación Media Absoluta (Nigrini MAD Score).")
    mad_conformity_level: str = Field(
        default="CONFORMIDAD_ACEPTABLE",
        description="Nivel Nigrini: CONFORMIDAD_ESTRECHA, CONFORMIDAD_ACEPTABLE, CONFORMIDAD_MARGINAL, NO_CONFORME_ANOMALO.",
    )
    is_distribution_suspicious: bool = Field(
        default=False,
        description="Verdadero si p-value < 0.05 o MAD indica no conformidad.",
    )
    first_digit_analysis: List[BenfordDigitDTO] = Field(default_factory=list)
    second_digit_analysis: List[BenfordDigitDTO] = Field(default_factory=list)
    top_two_digits_anomalies: List[BenfordDigitDTO] = Field(
        default_factory=list, description="Top 5 combinaciones de 2 dígitos (10-99) con mayor anomalía."
    )
    anomalous_digits: List[int] = Field(default_factory=list, description="Dígitos con desviaciones críticas.")
    analyzable_columns: List[str] = Field(
        default_factory=list, description="Lista de todas las columnas numéricas auditables en la tabla."
    )
