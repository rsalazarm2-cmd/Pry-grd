from typing import List, Optional
from pydantic import BaseModel, Field


class SegmentDefinitionDTO(BaseModel):
    """Definición de un segmento o atómico derivado de una columna compuesta."""
    index: int = Field(description="Índice posicional basado en 1 (1, 2, 3...)")
    suggested_alias: str = Field(description="Nombre o alias sugerido para el segmento atómico")
    sample_value: Optional[str] = Field(default=None, description="Valor de muestra extraído")


class AtomicitySuggestionDTO(BaseModel):
    """Sugerencia automática de atomización generada por el motor de análisis."""
    column_name: str = Field(description="Nombre de la columna en Bronce")
    suggested_clean_header: Optional[str] = Field(default=None, description="Nombre de columna saneado (ej: quitar TO_CHAR)")
    delimiter: str = Field(description="Delimitador detectado (., -, /, espacio, etc.)")
    confidence_score: float = Field(description="Nivel de confianza de la detección (0.0 a 1.0)")
    detected_segments_count: int = Field(description="Cantidad de segmentos atómicos detectados")
    suggested_segments: List[SegmentDefinitionDTO] = Field(default_factory=list)
    sample_raw_values: List[str] = Field(default_factory=list, description="Muestras crudas de la celda")


class ColumnSplitRuleDTO(BaseModel):
    """Regla de división/atomización configurada por el usuario para la Capa Plata."""
    column_name: str = Field(description="Nombre de la columna de origen")
    enabled: bool = Field(default=True, description="Si es True, se ejecuta el desglosado en la Capa Plata")
    delimiter: str = Field(default=".", description="Caracter delimitador a usar en split_part")
    keep_original: bool = Field(default=False, description="Si es True, conserva la columna original además de las atómicas")
    segments: List[SegmentDefinitionDTO] = Field(default_factory=list, description="Mapeo de índices a alias personalizados")


class AtomicityConfigDTO(BaseModel):
    """Contenedor global de sugerencias y reglas de atomización."""
    suggestions: List[AtomicitySuggestionDTO] = Field(default_factory=list)
    active_rules: List[ColumnSplitRuleDTO] = Field(default_factory=list)
