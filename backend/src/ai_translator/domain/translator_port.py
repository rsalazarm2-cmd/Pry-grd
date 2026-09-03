from abc import ABC, abstractmethod
from typing import List
from src.ai_translator.domain.models import SemanticMappingSuggestionDTO, TargetSchemaDefinitionDTO

class SemanticTranslatorPort(ABC):
    """
    Puerto (Interfaz) que define el contrato que cualquier traductor de IA 
    (sea por Embeddings, LLM, u otro) debe cumplir.
    """

    @abstractmethod
    def translate_columns(
        self,
        source_columns: List[str],
        target_schema: TargetSchemaDefinitionDTO,
        threshold: float = 0.5
    ) -> SemanticMappingSuggestionDTO:
        """
        Deduce el mapeo de columnas de origen al esquema destino.
        
        :param source_columns: Lista de nombres de columnas extraídas del archivo (Ej. ["FECHA", "DEBITO"]).
        :param target_schema: Definición del esquema esperado (Ej. {"CREATION_DATE": "Fecha de creación..."}).
        :param threshold: Puntaje mínimo de confianza (0 a 1) para aceptar un mapeo.
        :return: DTO con las sugerencias de mapeo, los scores y las columnas ignoradas.
        """
        pass
