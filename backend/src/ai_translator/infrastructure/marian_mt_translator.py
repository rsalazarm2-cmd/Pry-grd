from typing import List
from concurrent.futures import ThreadPoolExecutor
from transformers import MarianMTModel, MarianTokenizer

class MarianMTTranslator:
    def __init__(self, model_name: str = "Helsinki-NLP/opus-mt-en-es"):
        """
        Inicializa el traductor usando el modelo especializado de Helsinki.
        """
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)
        self.executor = ThreadPoolExecutor(max_workers=2)

    def _clean_column_name(self, col: str) -> str:
        """Limpia el nombre de la columna para mejorar la traducción."""
        return col.replace("_", " ").title()

    def _do_translate(self, cleaned_sources: List[str]) -> List[str]:
        inputs = self.tokenizer(cleaned_sources, return_tensors="pt", padding=True)
        translated = self.model.generate(**inputs)
        return [self.tokenizer.decode(t, skip_special_tokens=True) for t in translated]

    def translate(self, source_columns: List[str]) -> List[str]:
        """
        Traduce dinámicamente una lista de columnas del inglés al español (asíncrono en worker pool).
        """
        if not source_columns:
            return []
            
        cleaned_sources = [self._clean_column_name(c) for c in source_columns]
        future = self.executor.submit(self._do_translate, cleaned_sources)
        return future.result(timeout=30)

