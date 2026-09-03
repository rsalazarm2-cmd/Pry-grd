import re
from typing import List, Dict
from src.ai_translator.infrastructure.marian_mt_translator import MarianMTTranslator
from src.ai_translator.domain.models import SemanticMappingSuggestionDTO

class TranslateColumnsUseCase:
    """
    Caso de Uso que traduce libremente columnas del inglés al español
    y garantiza que los nombres resultantes sean únicos y válidos para bases de datos (slugified).
    """
    def __init__(self, translator: MarianMTTranslator):
        self.translator = translator

    def _slugify(self, text: str) -> str:
        import unicodedata
        # Remove accents
        text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
        # Replace non-alphanumeric with underscores
        text = re.sub(r'[^a-zA-Z0-9]+', '_', text)
        # Uppercase and strip trailing/leading underscores
        return text.strip('_').upper()

    def execute(self, source_columns: List[str], target_lang: str = "es") -> SemanticMappingSuggestionDTO:
        if not source_columns:
            return SemanticMappingSuggestionDTO(
                suggested_mapping={},
                confidence_scores={},
                unmapped_columns=[]
            )

        # 1. Translate
        translated_texts = self.translator.translate(source_columns)

        suggested_mapping: Dict[str, str] = {}
        seen_slugs = set()

        # 2. Slugify and Deduplicate
        for original, translated in zip(source_columns, translated_texts):
            base_slug = self._slugify(translated)
            
            # Si la traducción falló o devolvió vacío, usamos la columna original limpia
            if not base_slug:
                base_slug = self._slugify(original)
                if not base_slug:
                    base_slug = "COLUMNA"

            slug = base_slug
            counter = 2
            
            # Deduplication Loop
            while slug in seen_slugs:
                slug = f"{base_slug}_{counter}"
                counter += 1
                
            seen_slugs.add(slug)
            suggested_mapping[original] = slug

        # Since it translates everything dynamically, there are no unmapped columns.
        return SemanticMappingSuggestionDTO(
            suggested_mapping=suggested_mapping,
            confidence_scores={col: 1.0 for col in source_columns},
            unmapped_columns=[]
        )
