from typing import List
from src.ai_translator.domain.translator_port import SemanticTranslatorPort
from src.ai_translator.domain.models import SemanticMappingSuggestionDTO, TargetSchemaDefinitionDTO

class AutoMapColumnsUseCase:
    """
    Caso de Uso que orquesta la solicitud de traducción.
    En el futuro, podría inyectar distintos traductores (Embeddings, LLM, etc.)
    según la configuración.
    """
    def __init__(self, translator: SemanticTranslatorPort):
        self.translator = translator

    def execute(
        self,
        source_columns: List[str],
        target_schema: TargetSchemaDefinitionDTO,
        threshold: float = 0.4
    ) -> SemanticMappingSuggestionDTO:
        """
        Ejecuta la sugerencia de mapeo.
        :param source_columns: Columnas leídas del archivo CSV/Parquet.
        :param target_schema: Diccionario {columna_estandar: descripcion_del_negocio}.
        :param threshold: Umbral mínimo de similitud. (Bajado a 0.4 para ser más permisivo).
        """
        if not source_columns:
            return SemanticMappingSuggestionDTO(
                suggested_mapping={},
                confidence_scores={},
                unmapped_columns=[]
            )

        return self.translator.translate_columns(source_columns, target_schema, threshold)
