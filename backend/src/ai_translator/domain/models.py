from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class SemanticMappingSuggestionDTO(BaseModel):
    """
    Sugerencia de mapeo devuelta por el traductor de IA.
    Ejemplo: {"LIBRO": "LEDGER_NAME", "DEBITO": "ACCOUNTED_DR"}
    """
    suggested_mapping: Dict[str, str] = Field(
        ...,
        description="Mapeo donde la clave es la columna de origen y el valor es la columna estándar de destino."
    )
    confidence_scores: Optional[Dict[str, float]] = Field(
        None,
        description="Puntuación de confianza (0.0 a 1.0) para cada mapeo realizado."
    )
    unmapped_columns: Optional[List[str]] = Field(
        None,
        description="Columnas de origen que el modelo decidió ignorar (porque no corresponden a ningún estándar)."
    )

class TargetSchemaDefinitionDTO(BaseModel):
    """
    Define el esquema estándar al que queremos traducir.
    """
    schema_map: Dict[str, str] = Field(
        ...,
        description="Mapeo de nombre de columna estándar a su descripción semántica en lenguaje natural. Ej: {'LEDGER_NAME': 'El libro contable principal'}"
    )
